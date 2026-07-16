from functools import lru_cache

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.static import serve

from core.models import Image
from django_images.models import Image as StoredImage


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
    image_id = original_image_id_for_path(path)
    if image_id is not None:
        return HttpResponseRedirect(
            reverse('image-original', kwargs={'pk': image_id}),
        )
    return serve(
        request,
        path,
        document_root=settings.MEDIA_ROOT,
        show_indexes=False,
    )
