from django.dispatch import receiver
from django.db import models

from core.models import Image
from django_images.models import Thumbnail
from pinry_plugins import runner


@receiver(
    models.signals.pre_save,
    sender=Image,
    dispatch_uid="pinry_plugins.image_pre_creation",
)
def process_image_pre_creation(sender, instance: Image, **kwargs):
    # FIXME(winkidney): May have issue on determining if it
    #  is created or not
    if instance.pk is not None:
        return
    runner.run_image_pre_creation(instance)


@receiver(
    models.signals.pre_save,
    sender=Thumbnail,
    dispatch_uid="pinry_plugins.thumbnail_pre_creation",
)
def process_thumbnail_pre_creation(sender, instance: Thumbnail, **kwargs):
    # FIXME(winkidney): May have issue on determining if it
    #  is created or not
    if instance.pk is not None:
        return
    runner.run_thumbnail_pre_creation(instance)


def init():
    runner.get_plugin_instances()
