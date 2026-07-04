import shutil
import tempfile
from io import BytesIO

from django.test import TestCase
from django.test.utils import override_settings

import mock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework.test import APIClient
from rest_framework.reverse import reverse as drf_reverse

from .auth.backends import CombinedAuthBackend
from .models import User


def mock_requests_get(url, headers=None):
    response = mock.Mock(content=open('docs/src/imgs/logo-dark.png', 'rb').read())
    return response


class CombinedAuthBackendTest(TestCase):
    def setUp(self):
        self.backend = CombinedAuthBackend()
        self.username = 'jdoe'
        self.email = 'jdoe@example.com'
        self.password = 'password'
        User.objects.create_user(username=self.username, email=self.email, password=self.password)

    def test_authenticate_username(self):
        self.assertTrue(self.backend.authenticate(username=self.username, password=self.password))

    def test_authenticate_email(self):
        self.assertTrue(self.backend.authenticate(username=self.email, password=self.password))

    def test_authenticate_wrong_password(self):
        self.assertIsNone(self.backend.authenticate(username=self.username, password='wrong-password'))

    def test_authenticate_unknown_user(self):
        self.assertIsNone(self.backend.authenticate(username='wrong-username', password='wrong-password'))


class CreateUserTest(TestCase):
    def test_create_post(self):
        data = {
            'username': 'jdoe',
            'email': 'jdoe@example.com',
            'password': 'password',
            'password_repeat': 'password',
        }
        response = self.client.post(
            reverse('users:user-list'),
            data=data,
        )
        self.assertEqual(response.status_code, 201)

    @override_settings(ALLOW_NEW_REGISTRATIONS=False)
    def test_create_post_not_allowed(self):
        data = {
            'username': 'jdoe',
            'email': 'jdoe@example.com',
            'password': 'password',
            'password_repeat': 'password',

        }
        response = self.client.post(
            reverse('users:user-list'),
            data=data,
        )
        self.assertEqual(response.status_code, 401)


class LogoutViewTest(TestCase):
    def setUp(self):
        User.objects.create_user(username='jdoe', password='password')
        self.client.login(username='jdoe', password='password')

    def test_logout_view(self):
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 302)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.first_user = User.objects.create_user(username='jdoe', password='password')
        self.second_user = User.objects.create_user(username='judy', password='password')
        self.client.login(username='jdoe', password='password')

    def test_should_have_access_to_token(self):
        from rest_framework.authtoken.models import Token
        url = drf_reverse('users:public-user-list')
        response = self.client.get(f"{url}?username={self.first_user.username}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['token'], Token.objects.get(user=self.first_user).key)

    def test_should_have_no_access_to_token_of_other_user(self):
        url = drf_reverse('users:public-user-list')
        response = self.client.get(f"{url}?username={self.second_user.username}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['token'], None)


class AvatarUploadTest(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.user = User.objects.create_user(username='jdoe', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        shutil.rmtree(self.media_root)

    def make_image_file(self, name='avatar.png', size=(200, 120)):
        image = Image.new('RGB', size, color='red')
        image_bytes = BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        return SimpleUploadedFile(name, image_bytes.read(), content_type='image/png')

    def test_upload_avatar_creates_multiple_sizes(self):
        with self.settings(MEDIA_ROOT=self.media_root):
            url = drf_reverse('users:user-detail', args=[self.user.id])
            response = self.client.patch(
                url,
                {'avatar_file': self.make_image_file()},
                format='multipart',
            )

            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(response.data['avatar']['small'])
            self.assertIsNotNone(response.data['avatar']['medium'])
            self.assertIsNotNone(response.data['avatar']['large'])

            self.user.pinry_profile.refresh_from_db()
            self.assertEqual(self.user.pinry_profile.avatar_small.width, 30)
            self.assertEqual(self.user.pinry_profile.avatar_small.height, 30)
            self.assertEqual(self.user.pinry_profile.avatar_medium.width, 48)
            self.assertEqual(self.user.pinry_profile.avatar_medium.height, 48)
            self.assertEqual(self.user.pinry_profile.avatar_large.width, 96)
            self.assertEqual(self.user.pinry_profile.avatar_large.height, 96)

    def test_upload_avatar_rejects_files_larger_than_2mb(self):
        with self.settings(MEDIA_ROOT=self.media_root):
            url = drf_reverse('users:user-detail', args=[self.user.id])
            response = self.client.patch(
                url,
                {
                    'avatar_file': SimpleUploadedFile(
                        'large-avatar.jpg',
                        b'0' * (2 * 1024 * 1024 + 1),
                        content_type='image/jpeg',
                    )
                },
                format='multipart',
            )

            self.assertEqual(response.status_code, 400)
            self.assertIn('avatar_file', response.data)
