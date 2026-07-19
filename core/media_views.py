from functools import lru_cache
import posixpath
import time

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views.static import serve

from core.models import Image
from django_images.models import Image as StoredImage


_UNTHROTTLED_MEDIA_PREFIXES = (
    'avatars/',
    'motion/',
    '.upload-chunks/',
)


def canonical_media_path(path):
    """Match static serving's path normalization before any policy checks."""
    normalized_path = posixpath.normpath(
        str(path).replace('\\', '/')
    ).lstrip('/')
    if (
        normalized_path in ('', '.', '..')
        or normalized_path.startswith('../')
        or '\x00' in normalized_path
    ):
        raise Http404()
    return normalized_path


def is_thumbnail_media_path(path):
    """Return whether a public media path should use thumbnail pacing.

    ``IMAGE_PATH`` is configurable and the production setting currently puts
    originals and all generated image derivatives in the same hash-shaped
    directory.  The original is handled above by ``original_image_id_for_path``;
    every remaining image path is therefore a derivative unless it belongs to
    one of the explicitly separate media families below.
    """
    normalized_path = canonical_media_path(path)
    return not normalized_path.startswith(_UNTHROTTLED_MEDIA_PREFIXES)


def throttled_media_content(content, bytes_per_second):
    """Yield media chunks at a bounded per-response byte rate.

    The delay is applied before requesting the next chunk.  This avoids an
    unnecessary delay after the final chunk while still pacing the bytes that
    have already been yielded to the WSGI server.
    """
    if bytes_per_second <= 0:
        yield from content
        return

    iterator = iter(content)
    first_chunk = True
    delay = 0
    while True:
        if not first_chunk and delay:
            time.sleep(delay)
        try:
            chunk = next(iterator)
        except StopIteration:
            return
        yield chunk
        delay = len(chunk) / float(bytes_per_second)
        first_chunk = False


@lru_cache(maxsize=16384)
def original_image_id_for_path(path):
    return Image.objects.filter(image=path).values_list('pk', flat=True).first()


@receiver(
    post_save,
    sender=Image,
    dispatch_uid='clear_guarded_media_cache_after_proxy_save',
)
@receiver(
    post_delete,
    sender=Image,
    dispatch_uid='clear_guarded_media_cache_after_proxy_delete',
)
@receiver(
    post_save,
    sender=StoredImage,
    dispatch_uid='clear_guarded_media_cache_after_image_save',
)
@receiver(
    post_delete,
    sender=StoredImage,
    dispatch_uid='clear_guarded_media_cache_after_image_delete',
)
def clear_original_media_path_cache(**kwargs):
    original_image_id_for_path.cache_clear()


def serve_guarded_media(request, path):
    """Route stored originals through the permission-aware throttled stream."""
    path = canonical_media_path(path)
    image_id = original_image_id_for_path(path)
    if image_id is not None:
        return HttpResponseRedirect(
            reverse('image-original', kwargs={'pk': image_id}),
        )
    response = serve(
        request,
        path,
        document_root=settings.MEDIA_ROOT,
        show_indexes=False,
    )
    throttle_rate = getattr(
        settings,
        'IMAGE_THUMBNAIL_THROTTLE_BYTES_PER_SECOND',
        64 * 1024,
    )
    if (
        throttle_rate > 0
        and is_thumbnail_media_path(path)
        and getattr(response, 'streaming', False)
    ):
        response.streaming_content = throttled_media_content(
            response.streaming_content,
            throttle_rate,
        )
    return response
