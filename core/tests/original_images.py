import shutil
import tempfile
from io import BytesIO
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image as PILImage
from rest_framework.test import APITestCase

from core.media_views import original_image_id_for_path
from core.models import Image, Pin
from django_images.models import Thumbnail
from users.models import User


class OriginalImageDeliveryTests(APITestCase):
    def setUp(self):
        super(OriginalImageDeliveryTests, self).setUp()
        self.media_root = tempfile.mkdtemp()
        self.media_settings = override_settings(
            MEDIA_ROOT=self.media_root,
            IMAGE_PREVIEW_THROTTLE_BYTES_PER_SECOND=1024 * 1024,
        )
        self.media_settings.enable()
        original_image_id_for_path.cache_clear()
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

    def test_thumbnail_media_is_served_without_original_redirect(self):
        thumbnail_payload = self.image_bytes(color='blue')
        thumbnail = Thumbnail.objects.create(
            original=self.image,
            size='guard-test',
            image=SimpleUploadedFile(
                'thumbnail.png',
                thumbnail_payload,
                content_type='image/png',
            ),
        )

        response = self.client.get(thumbnail.image.url)
        body = b''.join(response.streaming_content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body, thumbnail_payload)
