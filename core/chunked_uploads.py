import hashlib
import math
import os

from datetime import timedelta

from django.conf import settings
from django.core.files import File
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.likes import _is_trusted_proxy, client_ip
from core.models import ChunkedUpload, UploadRateBucket
from core.serializers import ImageSerializer
from users.models import UserProfile
from users.serializers import AvatarImageField, UserSerializer


def upload_directory():
    return os.path.join(settings.MEDIA_ROOT, '.upload-chunks')


def upload_path(upload):
    return os.path.join(upload_directory(), '{}.part'.format(upload.id))


def ensure_upload_directory():
    path = upload_directory()
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
    return path


def delete_upload_file(upload):
    path = upload_path(upload)
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def cleanup_expired_uploads(limit=30):
    now = timezone.now()
    expired = list(
        ChunkedUpload.objects.filter(
            expires__lt=now,
        ).order_by('expires')[:limit]
    )
    for upload in expired:
        delete_upload_file(upload)
        upload.delete()
    UploadRateBucket.objects.filter(
        updated__lt=now - timedelta(days=2),
    ).delete()


def upload_ip_hash(request):
    remote_addr = request.META.get('REMOTE_ADDR', '')
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for and not _is_trusted_proxy(remote_addr):
        return ''
    identity = client_ip(request)
    if not identity:
        return ''
    secret = settings.SECRET_KEY.encode('utf-8')
    return hashlib.sha256(secret + identity.encode('utf-8')).hexdigest()


def actor_keys(upload):
    keys = ['user:{}'.format(upload.user_id)]
    if upload.ip_hash:
        keys.append('ip:{}'.format(upload.ip_hash))
    return tuple(keys)


def get_locked_bucket(actor_key, now):
    UploadRateBucket.objects.get_or_create(
        actor_key=actor_key,
        defaults={'available_at': now},
    )
    return UploadRateBucket.objects.select_for_update().get(
        actor_key=actor_key,
    )


def reserve_chunk_bandwidth(upload, chunk_size):
    bytes_per_second = getattr(
        settings,
        'IMAGE_UPLOAD_THROTTLE_BYTES_PER_SECOND',
        1024 * 1024,
    )
    if bytes_per_second <= 0:
        return 0
    now = timezone.now()
    duration_ms = max(1, int(math.ceil(
        (float(chunk_size) / bytes_per_second) * 1000,
    )))
    with transaction.atomic():
        buckets = [
            get_locked_bucket(actor_key, now)
            for actor_key in sorted(actor_keys(upload))
        ]
        wait_ms = max([
            max(0, int(math.ceil(
                (bucket.available_at - now).total_seconds() * 1000,
            )))
            for bucket in buckets
        ] or [0])
        if wait_ms > 0:
            return wait_ms
        available_at = now + timedelta(milliseconds=duration_ms)
        for bucket in buckets:
            bucket.available_at = available_at
            bucket.save(update_fields=['available_at', 'updated'])
    return 0


def next_chunk_after_ms(chunk_size):
    bytes_per_second = getattr(
        settings,
        'IMAGE_UPLOAD_THROTTLE_BYTES_PER_SECOND',
        1024 * 1024,
    )
    if bytes_per_second <= 0:
        return 0
    return max(1, int(math.ceil(
        (float(chunk_size) / bytes_per_second) * 1000,
    )))


def reconcile_upload_file(upload):
    if upload.status != ChunkedUpload.STATUS_UPLOADING:
        return upload
    path = upload_path(upload)
    actual_size = os.path.getsize(path) if os.path.exists(path) else 0
    if actual_size > upload.total_size:
        delete_upload_file(upload)
        actual_size = 0
    if upload.received_size != actual_size:
        upload.received_size = actual_size
        upload.save(update_fields=['received_size', 'updated'])
    return upload


def upload_processing_timed_out(upload, now=None):
    timeout_seconds = getattr(
        settings,
        'CHUNKED_UPLOAD_PROCESSING_TIMEOUT_SECONDS',
        15 * 60,
    )
    if timeout_seconds <= 0 or upload.status != ChunkedUpload.STATUS_PROCESSING:
        return False
    if now is None:
        now = timezone.now()
    return upload.updated <= now - timedelta(seconds=timeout_seconds)


def create_or_resume_upload(user, request, data):
    cleanup_expired_uploads()
    target = data.get('target')
    if target not in dict(ChunkedUpload.TARGET_CHOICES):
        raise ValidationError({'target': 'Unsupported upload target.'})
    try:
        total_size = int(data.get('total_size'))
    except (TypeError, ValueError):
        raise ValidationError({'total_size': 'A valid file size is required.'})
    max_size = (
        settings.CHUNKED_UPLOAD_MAX_AVATAR_SIZE
        if target == ChunkedUpload.TARGET_AVATAR
        else settings.CHUNKED_UPLOAD_MAX_IMAGE_SIZE
    )
    if total_size <= 0 or total_size > max_size:
        raise ValidationError({
            'total_size': 'File size must be between 1 and {} bytes.'.format(
                max_size,
            ),
        })
    raw_filename = str(data.get('filename') or 'upload').replace('\\', '/')
    filename = os.path.basename(raw_filename)[:255]
    if not filename or '\x00' in filename:
        raise ValidationError({'filename': 'A valid file name is required.'})
    content_type = str(data.get('content_type') or '')[:127]
    if content_type and not content_type.lower().startswith('image/'):
        raise ValidationError({'content_type': 'Only image uploads are supported.'})
    client_key = str(data.get('client_key') or '')[:96]
    existing = None
    if client_key:
        existing = ChunkedUpload.objects.filter(
            user=user,
            client_key=client_key,
            target=target,
            filename=filename,
            total_size=total_size,
            status__in=(
                ChunkedUpload.STATUS_UPLOADING,
                ChunkedUpload.STATUS_PROCESSING,
                ChunkedUpload.STATUS_COMPLETE,
            ),
            expires__gte=timezone.now(),
        ).order_by('-published').first()
    if existing is not None:
        return reconcile_upload_file(existing), False
    upload = ChunkedUpload.objects.create(
        user=user,
        target=target,
        filename=filename,
        content_type=content_type,
        total_size=total_size,
        client_key=client_key,
        ip_hash=upload_ip_hash(request),
        expires=timezone.now() + timedelta(
            seconds=settings.CHUNKED_UPLOAD_SESSION_AGE,
        ),
    )
    ensure_upload_directory()
    open(upload_path(upload), 'ab').close()
    return upload, True


def append_chunk(upload, offset, chunk):
    if upload.status != ChunkedUpload.STATUS_UPLOADING:
        raise ValidationError({'status': 'This upload cannot receive chunks.'})
    if offset != upload.received_size:
        raise ValidationError({
            'offset': 'Expected offset {}.'.format(upload.received_size),
        })
    chunk_size = len(chunk)
    max_chunk_size = settings.CHUNKED_UPLOAD_CHUNK_SIZE
    if chunk_size <= 0 or chunk_size > max_chunk_size:
        raise ValidationError({
            'chunk': 'Chunk size must be between 1 and {} bytes.'.format(
                max_chunk_size,
            ),
        })
    if upload.received_size + chunk_size > upload.total_size:
        raise ValidationError({'chunk': 'Chunk exceeds declared file size.'})
    ensure_upload_directory()
    path = upload_path(upload)
    actual_size = os.path.getsize(path) if os.path.exists(path) else 0
    if actual_size != upload.received_size:
        raise ValidationError({
            'offset': 'Stored upload offset is inconsistent; resume the upload.',
        })
    with open(path, 'ab') as stream:
        stream.write(chunk)
        stream.flush()
    upload.received_size += chunk_size
    upload.expires = timezone.now() + timedelta(
        seconds=settings.CHUNKED_UPLOAD_SESSION_AGE,
    )
    upload.save(update_fields=['received_size', 'expires', 'updated'])
    return upload


def complete_image_upload(upload, request, source_file):
    serializer = ImageSerializer(
        data={'image': source_file},
        context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    image = serializer.save()
    upload.image = image
    upload.save(update_fields=['image', 'updated'])
    return ImageSerializer(image, context={'request': request}).data


def complete_avatar_upload(upload, request, source_file):
    avatar_file = AvatarImageField().run_validation(source_file)
    profile, _ = UserProfile.objects.get_or_create(user=upload.user)
    profile.set_avatar(avatar_file)
    return UserSerializer(
        upload.user,
        context={'request': request},
    ).data


def completed_upload_result(upload, request):
    if upload.target == ChunkedUpload.TARGET_IMAGE:
        if not upload.image_id:
            raise ValidationError({
                'status': 'The completed image is no longer available.',
            })
        return ImageSerializer(
            upload.image,
            context={'request': request},
        ).data
    return UserSerializer(
        upload.user,
        context={'request': request},
    ).data


def mark_upload_complete(upload):
    with transaction.atomic():
        current = ChunkedUpload.objects.select_for_update().get(pk=upload.pk)
        if current.status == ChunkedUpload.STATUS_COMPLETE:
            return current
        if current.status != ChunkedUpload.STATUS_PROCESSING:
            raise ValidationError({
                'status': 'This upload is no longer processing.',
            })
        current.status = ChunkedUpload.STATUS_COMPLETE
        current.received_size = current.total_size
        current.expires = timezone.now() + timedelta(
            seconds=settings.CHUNKED_UPLOAD_SESSION_AGE,
        )
        current.save(update_fields=[
            'received_size',
            'status',
            'expires',
            'updated',
        ])
        return current


def mark_upload_failed(upload, error):
    try:
        with transaction.atomic():
            current = ChunkedUpload.objects.select_for_update().get(pk=upload.pk)
            if current.status != ChunkedUpload.STATUS_PROCESSING:
                return
            current.status = ChunkedUpload.STATUS_FAILED
            current.error = str(error)[:4096]
            current.save(update_fields=['status', 'error', 'updated'])
    except ChunkedUpload.DoesNotExist:
        return


def complete_upload(upload, request):
    completed = False
    failure = None
    should_process = False
    now = timezone.now()
    with transaction.atomic():
        upload = ChunkedUpload.objects.select_for_update().get(pk=upload.pk)
        upload = reconcile_upload_file(upload)
        if upload.status == ChunkedUpload.STATUS_COMPLETE:
            completed = True
        elif upload.status == ChunkedUpload.STATUS_PROCESSING:
            if not upload_processing_timed_out(upload, now):
                return None
            if (
                upload.target == ChunkedUpload.TARGET_IMAGE
                and upload.image_id
            ):
                upload.status = ChunkedUpload.STATUS_COMPLETE
                upload.expires = now + timedelta(
                    seconds=settings.CHUNKED_UPLOAD_SESSION_AGE,
                )
                upload.save(update_fields=['status', 'expires', 'updated'])
                completed = True
            else:
                upload.status = ChunkedUpload.STATUS_FAILED
                upload.error = 'Upload processing timed out.'
                upload.save(update_fields=['status', 'error', 'updated'])
                failure = 'Upload processing timed out. Please upload again.'
        elif upload.status == ChunkedUpload.STATUS_FAILED:
            failure = 'This upload failed processing.'
        elif upload.status == ChunkedUpload.STATUS_UPLOADING:
            if upload.received_size != upload.total_size:
                failure = (
                    'Upload is incomplete: {} of {} bytes received.'
                ).format(upload.received_size, upload.total_size)
            else:
                upload.status = ChunkedUpload.STATUS_PROCESSING
                upload.error = ''
                upload.save(update_fields=['status', 'error', 'updated'])
                should_process = True
    if failure is not None:
        raise ValidationError({'status': failure})
    if completed:
        return completed_upload_result(upload, request)
    if not should_process:
        raise ValidationError({'status': 'This upload cannot be completed.'})
    try:
        with open(upload_path(upload), 'rb') as stream:
            source_file = File(stream, name=upload.filename)
            if upload.target == ChunkedUpload.TARGET_AVATAR:
                result = complete_avatar_upload(upload, request, source_file)
            else:
                result = complete_image_upload(upload, request, source_file)
        mark_upload_complete(upload)
        delete_upload_file(upload)
        return result
    except Exception as exc:
        mark_upload_failed(upload, exc)
        raise
