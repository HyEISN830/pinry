import hashlib
import os
import PIL.Image
import requests
import uuid

from datetime import timedelta
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models, OperationalError, transaction
from django.dispatch import receiver
from django.utils import timezone

from core.motion_photo import extract_motion_photo_payload
from core.utils import motion_photo_upload_path
from django_images.models import Image as BaseImage, Thumbnail
from django_images import utils as image_utils
from taggit.managers import TaggableManager

from users.models import User


class ImageManager(models.Manager):
    _default_ua = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/48.0.2564.82 Safari/537.36',
    }

    @staticmethod
    def _is_valid_image(fp):
        fp.seek(0)
        try:
            PIL.Image.open(fp)
        except PIL.UnidentifiedImageError:
            fp.seek(0)
            return False
        else:
            fp.seek(0)
            return True

    def fetch_from_url(self, url, referer=None):
        file_name = url.split("/")[-1].split('#')[0].split('?')[0]
        buf = BytesIO()
        headers = dict(self._default_ua)
        if referer is not None:
            headers["Referer"] = referer
        response = requests.get(url, headers=headers)
        buf.write(response.content)
        if not self._is_valid_image(buf):
            return None
        obj = InMemoryUploadedFile(buf, 'image', file_name,
                                   None, buf.tell(), None)
        # create the image and its thumbnails in one transaction, removing
        # a chance of getting Database into a inconsistent state when we
        # try to create thumbnails one by one later
        image = self.create(image=obj)
        Thumbnail.objects.get_or_create_at_sizes(image, settings.IMAGE_SIZES.keys())
        image.get_animated_thumbnail()
        image.create_motion_photo()
        return image

    def create_for_url(self, url, referer=None):
        return self.fetch_from_url(url, referer)


class Image(BaseImage):
    objects = ImageManager()

    class Sizes:
        standard = "standard"
        medium = "medium"
        thumbnail = "thumbnail"
        square = "square"
        animated_thumbnail = "animated_thumbnail"

    class Meta:
        proxy = True

    @property
    def standard(self):
        return Thumbnail.objects.get(
            original=self, size=self.Sizes.standard
        )

    @property
    def medium(self):
        try:
            return Thumbnail.objects.get(
                original=self,
                size=self.Sizes.medium,
            )
        except Thumbnail.DoesNotExist:
            # Existing images predate the medium derivative. Serialize them
            # safely by creating it once on first access. Locking and checking
            # again inside the transaction avoids duplicate compression when
            # concurrent requests discover the missing row together.
            with transaction.atomic():
                locked_image = Image.objects.select_for_update().get(pk=self.pk)
                try:
                    return Thumbnail.objects.get(
                        original=locked_image,
                        size=self.Sizes.medium,
                    )
                except Thumbnail.DoesNotExist:
                    return Thumbnail.objects.get_or_create_at_sizes(
                        locked_image,
                        [self.Sizes.medium],
                    )[0]

    @property
    def thumbnail(self):
        return Thumbnail.objects.get(
            original=self, size=self.Sizes.thumbnail
        )

    @property
    def square(self):
        return Thumbnail.objects.get(
            original=self, size=self.Sizes.square
        )

    @property
    def animated_thumbnail(self):
        return self.get_animated_thumbnail()

    def is_gif(self):
        return self.image.name.lower().endswith('.gif')

    def is_jpeg(self):
        lower_name = self.image.name.lower()
        return lower_name.endswith('.jpg') or lower_name.endswith('.jpeg')

    def animated_thumbnail_size(self):
        return getattr(
            settings,
            'ANIMATED_GIF_THUMBNAIL_SIZE',
            self.Sizes.animated_thumbnail,
        )

    def get_animated_thumbnail(self):
        if not self.is_gif():
            return None
        try:
            return Thumbnail.objects.get(
                original=self, size=self.animated_thumbnail_size()
            )
        except Thumbnail.DoesNotExist:
            return self.create_animated_thumbnail()

    def create_animated_thumbnail(self):
        options = getattr(settings, 'ANIMATED_GIF_THUMBNAIL_OPTIONS', {})
        buf = image_utils.write_animated_gif_thumbnail_in_memory(
            self.image,
            options.get('size', [240, 0]),
            max_frames=options.get('max_frames', 24),
            crop=options.get('crop', False),
            upscale=options.get('upscale', False),
        )
        if buf is None:
            return None
        original_file = os.path.basename(self.image.name)
        base, ext = os.path.splitext(original_file)
        if ext.lower() != '.gif':
            original_file = '{}.gif'.format(base)
        thumb_file = InMemoryUploadedFile(
            buf,
            "image",
            original_file,
            "image/gif",
            buf.tell(),
            None,
        )
        thumbnail, _ = self.thumbnail_set.get_or_create(
            size=self.animated_thumbnail_size(),
            defaults={'image': thumb_file},
        )
        return thumbnail

    def get_motion_photo(self):
        try:
            return self.motion_asset
        except MotionPhoto.DoesNotExist:
            return None

    def create_motion_photo(self):
        motion_photo = self.get_motion_photo()
        if motion_photo is not None:
            return motion_photo
        if not self.is_jpeg():
            return None
        payload = extract_motion_photo_payload(self.image)
        if payload is None:
            return None
        motion_photo = MotionPhoto(
            image=self,
            video_length=payload.video_length,
            source=payload.source,
        )
        motion_photo._video_hash = hashlib.md5(payload.video).hexdigest()
        filename = '{}-motion.mp4'.format(os.path.splitext(
            os.path.basename(self.image.name),
        )[0])
        motion_photo.video.save(
            filename,
            ContentFile(payload.video),
            save=False,
        )
        motion_photo.save()
        return motion_photo


class ChunkedUpload(models.Model):
    TARGET_IMAGE = 'image'
    TARGET_AVATAR = 'avatar'
    TARGET_CHOICES = (
        (TARGET_IMAGE, TARGET_IMAGE),
        (TARGET_AVATAR, TARGET_AVATAR),
    )

    STATUS_UPLOADING = 'uploading'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETE = 'complete'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = (
        (STATUS_UPLOADING, STATUS_UPLOADING),
        (STATUS_PROCESSING, STATUS_PROCESSING),
        (STATUS_COMPLETE, STATUS_COMPLETE),
        (STATUS_FAILED, STATUS_FAILED),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        related_name='chunked_uploads',
        on_delete=models.CASCADE,
    )
    target = models.CharField(max_length=16, choices=TARGET_CHOICES)
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=127, blank=True)
    total_size = models.PositiveIntegerField()
    received_size = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_UPLOADING,
        db_index=True,
    )
    client_key = models.CharField(max_length=96, blank=True, db_index=True)
    ip_hash = models.CharField(max_length=96, blank=True, db_index=True)
    error = models.TextField(blank=True)
    image = models.ForeignKey(
        Image,
        blank=True,
        null=True,
        related_name='chunked_uploads',
        on_delete=models.CASCADE,
    )
    published = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    expires = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(
                fields=['user', 'status', 'updated'],
                name='core_chunk_user_status_idx',
            ),
            models.Index(
                fields=['ip_hash', 'status', 'updated'],
                name='core_chunk_ip_status_idx',
            ),
        ]


class UploadRateBucket(models.Model):
    actor_key = models.CharField(max_length=128, unique=True)
    available_at = models.DateTimeField()
    updated = models.DateTimeField(auto_now=True)


@receiver(models.signals.post_delete, sender=ChunkedUpload)
def delete_chunked_upload_file(sender, instance, **kwargs):
    path = os.path.join(
        settings.MEDIA_ROOT,
        '.upload-chunks',
        '{}.part'.format(instance.id),
    )
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


class MotionPhoto(models.Model):
    image = models.OneToOneField(
        BaseImage,
        related_name='motion_asset',
        on_delete=models.CASCADE,
    )
    video = models.FileField(upload_to=motion_photo_upload_path, max_length=255)
    video_length = models.PositiveIntegerField(default=0)
    source = models.CharField(max_length=64, blank=True)
    published = models.DateTimeField(auto_now_add=True)


@receiver(models.signals.post_delete, sender=MotionPhoto)
def delete_motion_photo_file(sender, instance, **kwargs):
    if getattr(settings, 'IMAGE_AUTO_DELETE', True):
        if instance.video.storage.exists(instance.video.name):
            instance.video.delete(save=False)


class Board(models.Model):
    class Meta:
        unique_together = ("submitter", "name")
        index_together = ("submitter", "name")

    submitter = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=False, null=False)
    private = models.BooleanField(default=False, blank=False)
    pins = models.ManyToManyField("Pin", related_name="pins", blank=True)

    published = models.DateTimeField(auto_now_add=True)


class Comic(models.Model):
    submitter = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=128, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    referer = models.CharField(null=True, blank=True, max_length=2048)
    private = models.BooleanField(default=False, blank=False)
    published = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager(blank=True)

    def tag_list(self):
        return self.tags.all()


class ComicPage(models.Model):
    class Meta:
        unique_together = ("comic", "order")
        ordering = ("order", "id")

    comic = models.ForeignKey(
        Comic,
        related_name="pages",
        on_delete=models.CASCADE,
    )
    image = models.ForeignKey(
        Image,
        blank=True,
        null=True,
        related_name="comic_pages",
        on_delete=models.CASCADE,
    )
    order = models.PositiveIntegerField()
    caption = models.TextField(blank=True, null=True)
    published = models.DateTimeField(auto_now_add=True)


class Pin(models.Model):
    submitter = models.ForeignKey(User, on_delete=models.CASCADE)
    private = models.BooleanField(default=False, blank=False)
    url = models.CharField(null=True, blank=True, max_length=2048)
    referer = models.CharField(null=True, blank=True, max_length=2048)
    description = models.TextField(blank=True, null=True)
    image = models.ForeignKey(
        Image,
        blank=True,
        null=True,
        related_name='pin',
        on_delete=models.CASCADE,
    )
    published = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()

    def tag_list(self):
        return self.tags.all()

    def __unicode__(self):
        return '%s - %s' % (self.submitter, self.published)


class ImageFetchJob(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_READY = 'ready'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = (
        (STATUS_PENDING, STATUS_PENDING),
        (STATUS_PROCESSING, STATUS_PROCESSING),
        (STATUS_READY, STATUS_READY),
        (STATUS_FAILED, STATUS_FAILED),
    )

    source_url = models.CharField(max_length=2048)
    referer = models.CharField(null=True, blank=True, max_length=2048)
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )
    image = models.ForeignKey(
        Image,
        blank=True,
        null=True,
        related_name='fetch_jobs',
        on_delete=models.SET_NULL,
    )
    pin = models.OneToOneField(
        Pin,
        blank=True,
        null=True,
        related_name='image_fetch_job',
        on_delete=models.CASCADE,
    )
    comic_page = models.OneToOneField(
        ComicPage,
        blank=True,
        null=True,
        related_name='image_fetch_job',
        on_delete=models.CASCADE,
    )
    error = models.TextField(blank=True)
    attempts = models.PositiveIntegerField(default=0)
    published = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    started = models.DateTimeField(blank=True, null=True)
    finished = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(
                fields=['status', 'published'],
                name='core_imgfetch_status_idx',
            ),
            models.Index(
                fields=['status', 'started'],
                name='core_imgfetch_stale_idx',
            ),
        ]

    @classmethod
    def enqueue_for_pin(cls, pin, source_url, referer=None):
        job, _ = cls.objects.update_or_create(
            pin=pin,
            defaults={
                'source_url': source_url,
                'referer': referer,
                'status': cls.STATUS_PENDING,
                'error': '',
                'image': None,
                'attempts': 0,
                'started': None,
                'finished': None,
            },
        )
        return job

    @classmethod
    def enqueue_for_comic_page(cls, comic_page, source_url, referer=None):
        job, _ = cls.objects.update_or_create(
            comic_page=comic_page,
            defaults={
                'source_url': source_url,
                'referer': referer,
                'status': cls.STATUS_PENDING,
                'error': '',
                'image': None,
                'attempts': 0,
                'started': None,
                'finished': None,
            },
        )
        return job

    @classmethod
    def reset_stale_processing(cls, timeout_seconds=None):
        if timeout_seconds is None:
            timeout_seconds = getattr(
                settings,
                'IMAGE_FETCH_PROCESSING_TIMEOUT_SECONDS',
                900,
            )
        if timeout_seconds <= 0:
            return 0
        cutoff = timezone.now() - timedelta(seconds=timeout_seconds)
        return cls.objects.filter(
            models.Q(started__lt=cutoff) | models.Q(started__isnull=True),
            status=cls.STATUS_PROCESSING,
        ).update(
            status=cls.STATUS_PENDING,
            error='Reset after worker processing timeout.',
            started=None,
            finished=None,
            updated=timezone.now(),
        )

    @classmethod
    def claim_next(cls):
        with transaction.atomic():
            job = cls.objects.filter(
                status=cls.STATUS_PENDING,
            ).order_by('published', 'id').first()
            if job is None:
                return None
            job.status = cls.STATUS_PROCESSING
            job.attempts += 1
            job.error = ''
            job.started = timezone.now()
            job.finished = None
            job.save(update_fields=[
                'status',
                'attempts',
                'error',
                'started',
                'finished',
                'updated',
            ])
            return job

    def process(self):
        try:
            image = Image.objects.fetch_from_url(self.source_url, self.referer)
            if image is None:
                raise ValueError('invalid image content')
            self.attach_image(image)
            self.image = image
            self.status = self.STATUS_READY
            self.error = ''
            self.finished = timezone.now()
            self.save(update_fields=[
                'image',
                'status',
                'error',
                'finished',
                'updated',
            ])
            return True
        except OperationalError as exc:
            self.status = self.STATUS_PENDING
            self.error = str(exc)[:4096]
            self.started = None
            self.finished = None
            self.save(update_fields=[
                'status',
                'error',
                'started',
                'finished',
                'updated',
            ])
            raise
        except Exception as exc:
            self.status = self.STATUS_FAILED
            self.error = str(exc)[:4096]
            self.finished = timezone.now()
            self.save(update_fields=['status', 'error', 'finished', 'updated'])
            return False

    def attach_image(self, image):
        if self.pin_id:
            Pin.objects.filter(pk=self.pin_id).update(image=image)
        if self.comic_page_id:
            ComicPage.objects.filter(pk=self.comic_page_id).update(image=image)


class PinLike(models.Model):
    class Meta:
        unique_together = ("pin", "actor_key")
        index_together = ("pin", "actor_key")
        indexes = [
            models.Index(
                fields=["ip_hash", "published"],
                name="core_pinlike_ip_pub_idx",
            ),
        ]

    pin = models.ForeignKey(Pin, related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    actor_key = models.CharField(max_length=96)
    ip_hash = models.CharField(max_length=96, blank=True)
    published = models.DateTimeField(auto_now_add=True)


class ComicLike(models.Model):
    class Meta:
        unique_together = ("comic", "actor_key")
        index_together = ("comic", "actor_key")
        indexes = [
            models.Index(
                fields=["ip_hash", "published"],
                name="core_comiclike_ip_pub_idx",
            ),
        ]

    comic = models.ForeignKey(
        Comic,
        related_name="likes",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    actor_key = models.CharField(max_length=96)
    ip_hash = models.CharField(max_length=96, blank=True)
    published = models.DateTimeField(auto_now_add=True)


class PinView(models.Model):
    """One de-duplicated view of a pin per viewer identity."""

    class Meta:
        unique_together = ("pin", "actor_key")
        index_together = ("pin", "actor_key")
        indexes = [
            models.Index(
                fields=["ip_hash", "published"],
                name="core_pinview_ip_pub_idx",
            ),
        ]

    pin = models.ForeignKey(Pin, related_name="views", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    actor_key = models.CharField(max_length=96)
    ip_hash = models.CharField(max_length=96, blank=True)
    published = models.DateTimeField(auto_now_add=True)


class ComicView(models.Model):
    """One de-duplicated view of a comic per viewer identity."""

    class Meta:
        unique_together = ("comic", "actor_key")
        index_together = ("comic", "actor_key")
        indexes = [
            models.Index(
                fields=["ip_hash", "published"],
                name="core_comicview_ip_pub_idx",
            ),
        ]

    comic = models.ForeignKey(
        Comic,
        related_name="views",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    actor_key = models.CharField(max_length=96)
    ip_hash = models.CharField(max_length=96, blank=True)
    published = models.DateTimeField(auto_now_add=True)


@receiver(models.signals.post_delete, sender=Pin)
def delete_pin_images(sender, instance, **kwargs):
    if instance.image_id is None:
        return
    try:
        image = instance.image
        if image.pin.exists() or image.comic_pages.exists():
            return
        image.delete()
    except Image.DoesNotExist:
        pass


@receiver(models.signals.post_delete, sender=ComicPage)
def delete_unused_comic_page_images(sender, instance, **kwargs):
    if instance.image_id is None:
        return
    try:
        image = instance.image
        if image.pin.exists() or image.comic_pages.exists():
            return
        image.delete()
    except Image.DoesNotExist:
        pass
