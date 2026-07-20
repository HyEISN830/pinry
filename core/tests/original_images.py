import os
import shutil
import tempfile
from io import BytesIO
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image as PILImage
from rest_framework.test import APITestCase

from core.media_views import (
    original_image_id_for_path,
    thumbnail_sizes_for_path,
    thumbnail_throttle_rate_for_path,
    throttled_media_content,
)
from core.models import Image, Pin
from core.serializers import ImageSerializer
from django_images.models import Thumbnail
from users.models import User


class OriginalImageDeliveryTests(APITestCase):
    def setUp(self):
        super(OriginalImageDeliveryTests, self).setUp()
        self.media_root = tempfile.mkdtemp()
        self.media_settings = override_settings(
            MEDIA_ROOT=self.media_root,
            IMAGE_PREVIEW_THROTTLE_BYTES_PER_SECOND=1024 * 1024,
            IMAGE_THUMBNAIL_THROTTLE_BYTES_PER_SECOND=64 * 1024,
        )
        self.media_settings.enable()
        original_image_id_for_path.cache_clear()
        thumbnail_sizes_for_path.cache_clear()
        self.owner = User.objects.create_user(
            username='original-owner',
            password='password',
        )
        self.original_payload = self.image_bytes(
            size=(256, 256),
            image_format='BMP',
        )
        self.image = Image.objects.create(
            image=SimpleUploadedFile(
                'original.bmp',
                self.original_payload,
                content_type='image/bmp',
            ),
        )
        self.pin = Pin.objects.create(
            submitter=self.owner,
            image=self.image,
            private=False,
        )

    def tearDown(self):
        original_image_id_for_path.cache_clear()
        thumbnail_sizes_for_path.cache_clear()
        Image.objects.all().delete()
        self.media_settings.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)
        super(OriginalImageDeliveryTests, self).tearDown()

    @staticmethod
    def image_bytes(size=(32, 24), image_format='PNG', color='red'):
        output = BytesIO()
        PILImage.new('RGB', size, color=color).save(
            output,
            format=image_format,
        )
        return output.getvalue()

    def test_raw_original_redirects_to_throttled_endpoint(self):
        response = self.client.get(self.image.image.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            reverse('image-original', kwargs={'pk': self.image.pk}),
        )

    def test_redirected_original_uses_stream_throttle(self):
        with mock.patch('core.views.time.sleep') as sleep:
            response = self.client.get(self.image.image.url, follow=True)
            body = b''.join(response.streaming_content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body, self.original_payload)
        self.assertTrue(sleep.called)
        total_delay = sum(call.args[0] for call in sleep.call_args_list)
        self.assertAlmostEqual(
            total_delay,
            len(self.original_payload) / (1024 * 1024),
        )

    def test_private_original_remains_hidden_after_redirect(self):
        self.pin.private = True
        self.pin.save(update_fields=['private'])

        response = self.client.get(self.image.image.url, follow=True)

        self.assertEqual(response.status_code, 404)

    def test_private_original_alias_path_remains_guarded(self):
        self.pin.private = True
        self.pin.save(update_fields=['private'])
        alias_url = '/media/avatars/../{}'.format(self.image.image.name)

        response = self.client.get(alias_url, follow=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.redirect_chain,
            [(reverse('image-original', kwargs={'pk': self.image.pk}), 302)],
        )

    def test_thumbnail_media_is_served_without_original_redirect(self):
        thumbnail_payload = self.image_bytes(
            size=(128, 128),
            image_format='BMP',
            color='blue',
        )
        thumbnail = Thumbnail.objects.create(
            original=self.image,
            size='guard-test',
            image=SimpleUploadedFile(
                'thumbnail.bmp',
                thumbnail_payload,
                content_type='image/bmp',
            ),
        )

        with mock.patch('core.media_views.time.sleep') as sleep:
            response = self.client.get(thumbnail.image.url)
            body = b''.join(response.streaming_content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body, thumbnail_payload)
        self.assertTrue(sleep.called)
        self.assertGreater(
            sum(call.args[0] for call in sleep.call_args_list),
            0,
        )

    def test_thumbnail_variants_use_size_specific_throttle_rates(self):
        expected_rates = {
            'thumbnail': 64 * 1024,
            'medium': 128 * 1024,
            'standard': 256 * 1024,
            'square': 64 * 1024,
            'animated_thumbnail_fast': 256 * 1024,
        }
        colors = {
            'thumbnail': 'red',
            'medium': 'green',
            'standard': 'blue',
            'square': 'yellow',
            'animated_thumbnail_fast': 'purple',
        }

        for size, expected_rate in expected_rates.items():
            with self.subTest(size=size):
                payload = self.image_bytes(
                    size=(128, 128),
                    image_format='BMP',
                    color=colors[size],
                )
                thumbnail = Thumbnail.objects.create(
                    original=self.image,
                    size=size,
                    image=SimpleUploadedFile(
                        '{}.bmp'.format(size),
                        payload,
                        content_type='image/bmp',
                    ),
                )

                self.assertEqual(
                    thumbnail_throttle_rate_for_path(thumbnail.image.name),
                    expected_rate,
                )
                with mock.patch(
                    'core.media_views.throttled_media_content',
                    wraps=throttled_media_content,
                ) as throttle:
                    response = self.client.get(thumbnail.image.url)
                    body = b''.join(response.streaming_content)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(body, payload)
                self.assertEqual(throttle.call_count, 1)
                self.assertEqual(throttle.call_args.args[1], expected_rate)

    def test_thumbnail_rate_cache_is_invalidated_when_derivative_changes(self):
        payload = self.image_bytes(
            size=(128, 128),
            image_format='BMP',
            color='orange',
        )
        thumbnail = Thumbnail.objects.create(
            original=self.image,
            size='medium',
            image=SimpleUploadedFile(
                'cached-medium.bmp',
                payload,
                content_type='image/bmp',
            ),
        )
        path = thumbnail.image.name

        self.assertEqual(thumbnail_sizes_for_path(path), ('medium',))
        thumbnail.delete()
        self.assertEqual(thumbnail_sizes_for_path(path), ())

    def test_legacy_image_medium_is_lazily_generated_and_serialized(self):
        Thumbnail.objects.get_or_create_at_sizes(
            self.image,
            ['thumbnail', 'standard', 'square'],
        )
        self.assertFalse(
            Thumbnail.objects.filter(
                original=self.image,
                size='medium',
            ).exists(),
        )

        first = self.image.medium
        second = self.image.medium

        self.assertEqual(first.pk, second.pk)
        self.assertEqual(
            Thumbnail.objects.filter(
                original=self.image,
                size='medium',
            ).count(),
            1,
        )
        serialized = ImageSerializer(self.image).data
        self.assertIsNotNone(serialized['medium'])

    def test_avatar_media_is_not_treated_as_a_thumbnail(self):
        avatar_payload = b'avatar-payload' * 512
        avatar_path = 'avatars/test/avatar.png'
        avatar_file = os.path.join(self.media_root, *avatar_path.split('/'))
        os.makedirs(os.path.dirname(avatar_file), exist_ok=True)
        with open(avatar_file, 'wb') as stream:
            stream.write(avatar_payload)

        with mock.patch('core.media_views.time.sleep') as sleep:
            response = self.client.get('/media/' + avatar_path)
            body = b''.join(response.streaming_content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body, avatar_payload)
        sleep.assert_not_called()
