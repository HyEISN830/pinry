import shutil
import tempfile
from datetime import timedelta
from io import BytesIO

from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image as PILImage
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import ChunkedUpload, Image
from users.models import User


class ChunkedUploadEndpointTests(APITestCase):
    def setUp(self):
        super(ChunkedUploadEndpointTests, self).setUp()
        self.media_root = tempfile.mkdtemp()
        self.user = User.objects.create_user(
            username='chunked-upload',
            password='password',
        )
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        shutil.rmtree(self.media_root, ignore_errors=True)
        super(ChunkedUploadEndpointTests, self).tearDown()

    @staticmethod
    def image_bytes(size=(48, 32), image_format='PNG'):
        output = BytesIO()
        PILImage.new('RGB', size, color='red').save(
            output,
            format=image_format,
        )
        return output.getvalue()

    def create_upload(self, payload, target='image', client_key='test-upload'):
        return self.client.post(
            reverse('upload-list'),
            {
                'target': target,
                'filename': 'test.png',
                'content_type': 'image/png',
                'total_size': len(payload),
                'client_key': client_key,
            },
            format='json',
            REMOTE_ADDR='198.51.100.10',
        )

    def put_chunk(self, upload_id, offset, chunk):
        return self.client.put(
            reverse('upload-chunk', kwargs={'pk': upload_id}),
            data=chunk,
            content_type='application/octet-stream',
            HTTP_X_UPLOAD_LENGTH=str(len(chunk)),
            HTTP_X_UPLOAD_OFFSET=str(offset),
            REMOTE_ADDR='198.51.100.10',
        )

    @override_settings(
        CHUNKED_UPLOAD_CHUNK_SIZE=64,
        IMAGE_UPLOAD_THROTTLE_BYTES_PER_SECOND=0,
    )
    def test_image_upload_tracks_confirmed_chunks_and_completes(self):
        with override_settings(MEDIA_ROOT=self.media_root):
            payload = self.image_bytes()
            created = self.create_upload(payload)

            self.assertEqual(created.status_code, status.HTTP_201_CREATED)
            upload_id = created.data['id']
            offset = 0
            while offset < len(payload):
                chunk = payload[offset:offset + 64]
                response = self.put_chunk(upload_id, offset, chunk)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                offset += len(chunk)
                self.assertEqual(response.data['received_size'], offset)

            completed = self.client.post(
                reverse('upload-complete', kwargs={'pk': upload_id}),
            )

            self.assertEqual(completed.status_code, status.HTTP_200_OK)
            image = Image.objects.get(pk=completed.data['result']['id'])
            self.assertEqual(image.width, 48)
            self.assertEqual(image.height, 32)

            repeated = self.client.post(
                reverse('upload-complete', kwargs={'pk': upload_id}),
            )

            self.assertEqual(repeated.status_code, status.HTTP_200_OK)
            self.assertEqual(
                repeated.data['result']['id'],
                completed.data['result']['id'],
            )

    @override_settings(
        CHUNKED_UPLOAD_CHUNK_SIZE=64,
        IMAGE_UPLOAD_THROTTLE_BYTES_PER_SECOND=0,
    )
    def test_create_with_same_client_key_resumes_confirmed_offset(self):
        with override_settings(MEDIA_ROOT=self.media_root):
            payload = self.image_bytes()
            created = self.create_upload(payload, client_key='resume-me')
            upload_id = created.data['id']
            response = self.put_chunk(upload_id, 0, payload[:32])
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            resumed = self.create_upload(payload, client_key='resume-me')

            self.assertEqual(resumed.status_code, status.HTTP_200_OK)
            self.assertEqual(resumed.data['id'], upload_id)
            self.assertEqual(resumed.data['received_size'], 32)

    @override_settings(
        CHUNKED_UPLOAD_CHUNK_SIZE=64,
        IMAGE_UPLOAD_THROTTLE_BYTES_PER_SECOND=64,
    )
    def test_rate_limit_returns_retry_delay_before_reading_next_chunk(self):
        with override_settings(MEDIA_ROOT=self.media_root):
            payload = self.image_bytes()
            created = self.create_upload(payload, client_key='rate-limited')
            upload_id = created.data['id']
            first = self.put_chunk(upload_id, 0, payload[:32])
            self.assertEqual(first.status_code, status.HTTP_200_OK)

            second = self.put_chunk(upload_id, 32, payload[32:64])

            self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
            self.assertGreater(second.data['retry_after_ms'], 0)
            self.assertEqual(second.data['received_size'], 32)

    @override_settings(
        CHUNKED_UPLOAD_CHUNK_SIZE=64,
        IMAGE_UPLOAD_THROTTLE_BYTES_PER_SECOND=0,
    )
    def test_offset_conflict_returns_server_offset(self):
        with override_settings(MEDIA_ROOT=self.media_root):
            payload = self.image_bytes()
            created = self.create_upload(payload, client_key='offset-conflict')

            response = self.put_chunk(created.data['id'], 12, payload[:32])

            self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
            self.assertEqual(response.data['received_size'], 0)

    @override_settings(
        CHUNKED_UPLOAD_CHUNK_SIZE=64,
        IMAGE_UPLOAD_THROTTLE_BYTES_PER_SECOND=0,
    )
    def test_avatar_upload_generates_avatar_variants(self):
        with override_settings(MEDIA_ROOT=self.media_root):
            payload = self.image_bytes(size=(160, 120))
            created = self.create_upload(
                payload,
                target='avatar',
                client_key='avatar-upload',
            )
            upload_id = created.data['id']
            offset = 0
            while offset < len(payload):
                chunk = payload[offset:offset + 64]
                response = self.put_chunk(upload_id, offset, chunk)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                offset += len(chunk)

            completed = self.client.post(
                reverse('upload-complete', kwargs={'pk': upload_id}),
            )

            self.assertEqual(completed.status_code, status.HTTP_200_OK)
            self.assertIsNotNone(completed.data['result']['avatar']['small'])
            self.assertIsNotNone(completed.data['result']['avatar']['medium'])
            self.assertIsNotNone(completed.data['result']['avatar']['large'])
            self.user.pinry_profile.refresh_from_db()
            self.assertEqual(self.user.pinry_profile.avatar_large.width, 96)

    def test_upload_sessions_are_private_to_their_owner(self):
        with override_settings(MEDIA_ROOT=self.media_root):
            payload = self.image_bytes()
            created = self.create_upload(payload, client_key='private-session')
            other_user = User.objects.create_user(
                username='other-upload-user',
                password='password',
            )
            self.client.force_authenticate(user=other_user)

            response = self.client.get(
                reverse('upload-detail', kwargs={'pk': created.data['id']}),
            )

            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertTrue(ChunkedUpload.objects.filter(
                pk=created.data['id'],
                user=self.user,
            ).exists())

    @override_settings(
        CHUNKED_UPLOAD_PROCESSING_TIMEOUT_SECONDS=1,
        IMAGE_UPLOAD_THROTTLE_BYTES_PER_SECOND=0,
    )
    def test_stale_processing_session_fails_instead_of_polling_forever(self):
        with override_settings(MEDIA_ROOT=self.media_root):
            payload = self.image_bytes()
            created = self.create_upload(payload, client_key='stale-processing')
            upload_id = created.data['id']
            ChunkedUpload.objects.filter(pk=upload_id).update(
                received_size=len(payload),
                status=ChunkedUpload.STATUS_PROCESSING,
                updated=timezone.now() - timedelta(seconds=2),
            )

            completed = self.client.post(
                reverse('upload-complete', kwargs={'pk': upload_id}),
            )

            self.assertEqual(completed.status_code, status.HTTP_400_BAD_REQUEST)
            upload = ChunkedUpload.objects.get(pk=upload_id)
            self.assertEqual(upload.status, ChunkedUpload.STATUS_FAILED)
