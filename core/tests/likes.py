from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.likes import (
    anonymous_like_actor_key,
    client_ip,
    legacy_like_actor_key,
    like_actor_keys,
    like_ip_hash,
)
from core.models import PinLike
from core.throttles import LikeDailyRateThrottle, LikeMinuteRateThrottle
from core.views import ComicViewSet, PinViewSet

from .helpers import create_image, create_pin, create_user


class LikeIdentityTests(TestCase):
    def setUp(self):
        super(LikeIdentityTests, self).setUp()
        self.factory = RequestFactory()

    def _request(self, **meta):
        request = self.factory.get('/', **meta)
        request.user = AnonymousUser()
        return request

    @override_settings(TRUSTED_PROXY_IPS=())
    def test_client_ip_ignores_forwarded_for_without_trusted_proxy(self):
        request = self._request(
            REMOTE_ADDR='198.51.100.10',
            HTTP_X_FORWARDED_FOR='203.0.113.20',
        )

        self.assertEqual(client_ip(request), '198.51.100.10')

    @override_settings(TRUSTED_PROXY_IPS=('198.51.100.10',))
    def test_client_ip_reads_forwarded_for_from_trusted_proxy(self):
        request = self._request(
            REMOTE_ADDR='198.51.100.10',
            HTTP_X_FORWARDED_FOR='203.0.113.20, 198.51.100.30',
        )

        self.assertEqual(client_ip(request), '203.0.113.20')

    @override_settings(TRUSTED_PROXY_IPS=('198.51.100.0/24',))
    def test_client_ip_supports_trusted_proxy_cidr(self):
        request = self._request(
            REMOTE_ADDR='198.51.100.10',
            HTTP_X_FORWARDED_FOR='203.0.113.21',
        )

        self.assertEqual(client_ip(request), '203.0.113.21')

    def test_anonymous_actor_keys_include_versioned_and_legacy_keys(self):
        request = self._request(REMOTE_ADDR='198.51.100.11')

        actor_key = anonymous_like_actor_key(request)
        keys = like_actor_keys(request)

        self.assertTrue(actor_key.startswith('anon:v1:'))
        self.assertIn(actor_key, keys)
        self.assertIn(legacy_like_actor_key(request), keys)


class LikeThrottleConfigTests(TestCase):
    def test_like_actions_use_like_throttles(self):
        expected = [LikeMinuteRateThrottle, LikeDailyRateThrottle]

        self.assertEqual(PinViewSet.like.kwargs['throttle_classes'], expected)
        self.assertEqual(ComicViewSet.like.kwargs['throttle_classes'], expected)


class LikeEndpointTests(APITestCase):
    def setUp(self):
        super(LikeEndpointTests, self).setUp()
        self.user = create_user('likes')
        self.pin = create_pin(self.user, create_image(), [])
        self.url = reverse('pin-like', kwargs={'pk': self.pin.pk})

    def test_anonymous_like_uses_versioned_actor_key(self):
        response = self.client.post(self.url, REMOTE_ADDR='198.51.100.20')

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(response.data['liked'])
        like = PinLike.objects.get(pin=self.pin)
        self.assertTrue(like.actor_key.startswith('anon:v1:'))

    def test_like_toggle_recognizes_legacy_ip_actor_key(self):
        request = RequestFactory().post('/', REMOTE_ADDR='198.51.100.21')
        request.user = AnonymousUser()
        PinLike.objects.create(
            pin=self.pin,
            actor_key=legacy_like_actor_key(request),
            ip_hash=like_ip_hash(request),
        )

        response = self.client.post(self.url, REMOTE_ADDR='198.51.100.21')

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertFalse(response.data['liked'])
        self.assertEqual(PinLike.objects.filter(pin=self.pin).count(), 0)
