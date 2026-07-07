import os
import PIL.Image
import requests

from io import BytesIO

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.dispatch import receiver

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

    # FIXME: Move this into an asynchronous task
    def create_for_url(self, url, referer=None):
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
        return image


class Image(BaseImage):
    objects = ImageManager()

    class Sizes:
        standard = "standard"
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
    image = models.ForeignKey(Image, related_name='pin', on_delete=models.CASCADE)
    published = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()

    def tag_list(self):
        return self.tags.all()

    def __unicode__(self):
        return '%s - %s' % (self.submitter, self.published)


@receiver(models.signals.post_delete, sender=Pin)
def delete_pin_images(sender, instance, **kwargs):
    try:
        image = instance.image
        if image.pin.exists() or image.comic_pages.exists():
            return
        image.delete()
    except Image.DoesNotExist:
        pass


@receiver(models.signals.post_delete, sender=ComicPage)
def delete_unused_comic_page_images(sender, instance, **kwargs):
    try:
        image = instance.image
        if image.pin.exists() or image.comic_pages.exists():
            return
        image.delete()
    except Image.DoesNotExist:
        pass
