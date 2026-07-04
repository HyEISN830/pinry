import hashlib
import os
import uuid

from django.conf import settings
from django.core.files.base import ContentFile
from django.contrib.auth.models import User as BaseUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_images import utils


AVATAR_FIELD_BY_SIZE = {
    'small': 'avatar_small',
    'medium': 'avatar_medium',
    'large': 'avatar_large',
}


def avatar_upload_path(instance, filename, **kwargs):
    _, ext = os.path.splitext(filename)
    user_id = instance.user_id or 'new'
    return 'avatars/{}/{}{}'.format(
        user_id,
        uuid.uuid4().hex,
        ext.lower(),
    )


def create_token_if_necessary(user: BaseUser):
    from rest_framework.authtoken.models import Token
    token = Token.objects.filter(user=user).first()
    if token is not None:
        return token
    else:
        return Token.objects.create(user=user)


class User(BaseUser):

    @property
    def gravatar(self):
        return hashlib.md5(self.email.encode('utf-8')).hexdigest()

    class Meta:
        proxy = True


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='pinry_profile',
        on_delete=models.CASCADE,
    )
    avatar = models.ImageField(upload_to=avatar_upload_path, max_length=255, blank=True)
    avatar_small = models.ImageField(upload_to=avatar_upload_path, max_length=255, blank=True)
    avatar_medium = models.ImageField(upload_to=avatar_upload_path, max_length=255, blank=True)
    avatar_large = models.ImageField(upload_to=avatar_upload_path, max_length=255, blank=True)

    def avatar_file_names(self):
        names = []
        for field_name in ['avatar'] + list(AVATAR_FIELD_BY_SIZE.values()):
            image = getattr(self, field_name)
            if image and image.name:
                names.append((image.storage, image.name))
        return names

    def delete_avatar_files(self, files):
        current_names = {
            name for _, name in self.avatar_file_names()
        }
        for storage, name in files:
            if name not in current_names and storage.exists(name):
                storage.delete(name)

    def set_avatar(self, avatar_file):
        old_files = self.avatar_file_names()
        self.avatar = avatar_file
        self.save(update_fields=['avatar'])
        self.create_avatar_thumbnails()
        self.delete_avatar_files(old_files)

    def create_avatar_thumbnails(self):
        if not self.avatar:
            return

        base, ext = os.path.splitext(os.path.basename(self.avatar.name))
        with utils.open_django_file(self.avatar) as avatar:
            source = utils.Image.open(avatar)
            source.load()
            for size_name, options in settings.AVATAR_SIZES.items():
                thumb = utils.scale_and_crop_single(source, **options)
                buf = utils.write_image_in_memory(thumb)
                field_name = AVATAR_FIELD_BY_SIZE[size_name]
                file_name = '{}_{}{}'.format(base, size_name, ext)
                getattr(self, field_name).save(
                    file_name,
                    ContentFile(buf.getvalue()),
                    save=False,
                )
        self.save(update_fields=list(AVATAR_FIELD_BY_SIZE.values()))


@receiver(post_save, sender=User)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance: User, **kwargs):
    create_token_if_necessary(instance)
    UserProfile.objects.get_or_create(user=instance)
