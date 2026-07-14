from django.conf import settings
from django.contrib.auth import login
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import AVATAR_FIELD_BY_SIZE, User, UserProfile, create_token_if_necessary


class AvatarImageField(serializers.ImageField):
    default_error_messages = {
        'max_size': 'Cropped avatar cannot be larger than 2MB.',
    }

    def to_internal_value(self, data):
        if data.size > settings.AVATAR_MAX_UPLOAD_SIZE:
            self.fail('max_size')
        return super(AvatarImageField, self).to_internal_value(data)


def get_file_url(request, field):
    if not field:
        return None
    return field.url


def get_avatar_data(user, request):
    try:
        profile = user.pinry_profile
    except UserProfile.DoesNotExist:
        return {
            'original': None,
            'small': None,
            'medium': None,
            'large': None,
        }

    avatar = {
        'original': get_file_url(request, profile.avatar),
    }
    for size_name, field_name in AVATAR_FIELD_BY_SIZE.items():
        avatar[size_name] = get_file_url(request, getattr(profile, field_name))
    return avatar


class PublicUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'gravatar',
            'avatar',
            settings.DRF_URL_FIELD_NAME,
        )
        extra_kwargs = {
            settings.DRF_URL_FIELD_NAME: {
                "view_name": "public-users:user-detail",
            },
        }

    avatar = serializers.SerializerMethodField(read_only=True)

    def get_avatar(self, obj: User):
        return get_avatar_data(obj, self.context.get('request'))


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'token',
            'email',
            'gravatar',
            'avatar',
            'avatar_file',
            'password',
            'password_repeat',
            settings.DRF_URL_FIELD_NAME,
        )
        extra_kwargs = {
            settings.DRF_URL_FIELD_NAME: {
                "view_name": "users:user-detail",
            },
        }

    password = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        min_length=6,
        max_length=32,
    )
    password_repeat = serializers.CharField(
        write_only=True,
        required=True,
        allow_blank=False,
        min_length=6,
        max_length=32,
    )
    token = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)
    avatar_file = AvatarImageField(write_only=True, required=False)

    def create(self, validated_data):
        avatar_file = validated_data.pop('avatar_file', None)
        if validated_data['password'] != validated_data['password_repeat']:
            raise ValidationError(
                detail={
                    "password_repeat": "Tow password doesn't match",
                }
            )
        validated_data.pop('password_repeat')
        password = validated_data.pop('password')
        user = super(UserSerializer, self).create(
            validated_data,
        )
        user.set_password(password)
        user.save()
        login(
            self.context['request'],
            user=user,
            backend=settings.AUTHENTICATION_BACKENDS[0],
        )
        if avatar_file is not None:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.set_avatar(avatar_file)
        return user

    def update(self, instance, validated_data):
        avatar_file = validated_data.pop('avatar_file', None)
        if validated_data:
            raise ValidationError(
                detail={
                    field: "This field cannot be updated here."
                    for field in validated_data.keys()
                }
            )
        user = instance
        if avatar_file is not None:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.set_avatar(avatar_file)
        return user

    def get_token(self, obj: User):
        if self.context['request'].user == obj:
            return create_token_if_necessary(obj).key
        return None

    def get_avatar(self, obj: User):
        return get_avatar_data(obj, self.context.get('request'))
