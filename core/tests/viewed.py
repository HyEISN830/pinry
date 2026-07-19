from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.likes import legacy_like_actor_key, like_ip_hash
from core.models import ComicView, PinView
from core.throttles import ViewDailyRateThrottle, ViewMinuteRateThrottle
from core.views import ComicViewSet, PinViewSet

from .helpers import create_image, create_pin, create_user


class ViewedThrottleConfigTests(APITestCase):
    def test_view_actions_use_independent_view_throttles(self):
        expected = [ViewMinuteRateThrottle, ViewDailyRateThrottle]

        self.assertEqual(PinViewSet.viewed.kwargs['throttle_classes'], expected)
        self.assertEqual(ComicViewSet.viewed.kwargs['throttle_classes'], expected)


class ViewedEndpointTests(APITestCase):
    def setUp(self):
        super(ViewedEndpointTests, self).setUp()
        self.user = create_user('viewed')
        self.pin = create_pin(self.user, create_image(), [])
        self.url = reverse('pin-viewed', kwargs={'pk': self.pin.pk})

    def test_anonymous_view_is_recorded_and_returned_in_pin_payload(self):
        response = self.client.post(self.url, REMOTE_ADDR='198.51.100.40')

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(response.data['viewed'])
        self.assertTrue(response.data['viewer_viewed'])
        self.assertEqual(response.data['viewed_count'], 1)
        self.assertEqual(PinView.objects.filter(pin=self.pin).count(), 1)

        detail = self.client.get(
            reverse('pin-detail', kwargs={'pk': self.pin.pk}),
            REMOTE_ADDR='198.51.100.40',
        )
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data['viewed_count'], 1)
        self.assertTrue(detail.data['viewer_viewed'])

    def test_repeated_anonymous_view_from_same_identity_is_deduplicated(self):
        first = self.client.post(self.url, REMOTE_ADDR='198.51.100.41')
        second = self.client.post(self.url, REMOTE_ADDR='198.51.100.41')

        self.assertEqual(first.data['viewed_count'], 1)
        self.assertEqual(second.data['viewed_count'], 1)
        self.assertEqual(PinView.objects.filter(pin=self.pin).count(), 1)

    def test_distinct_anonymous_identity_increments_count(self):
        self.client.post(self.url, REMOTE_ADDR='198.51.100.42')
        response = self.client.post(self.url, REMOTE_ADDR='198.51.100.43')

        self.assertEqual(response.data['viewed_count'], 2)
        self.assertEqual(PinView.objects.filter(pin=self.pin).count(), 2)

    def test_view_recognizes_same_legacy_actor_key_as_likes(self):
        request = RequestFactory().post('/', REMOTE_ADDR='198.51.100.45')
        request.user = AnonymousUser()
        PinView.objects.create(
            pin=self.pin,
            actor_key=legacy_like_actor_key(request),
            ip_hash=like_ip_hash(request),
        )

        response = self.client.post(self.url, REMOTE_ADDR='198.51.100.45')

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['viewed_count'], 1)
        self.assertEqual(PinView.objects.filter(pin=self.pin).count(), 1)


class ComicViewedEndpointTests(APITestCase):
    def setUp(self):
        super(ComicViewedEndpointTests, self).setUp()
        self.user = create_user('comic-viewed')
        from core.models import Comic
        self.comic = Comic.objects.create(
            submitter=self.user,
            title='Viewed comic',
            private=False,
        )
        self.url = reverse('comic-viewed', kwargs={'pk': self.comic.pk})

    def test_comic_view_is_idempotent(self):
        first = self.client.post(self.url, REMOTE_ADDR='198.51.100.44')
        second = self.client.post(self.url, REMOTE_ADDR='198.51.100.44')

        self.assertEqual(first.status_code, status.HTTP_200_OK, first.data)
        self.assertEqual(second.status_code, status.HTTP_200_OK, second.data)
        self.assertEqual(second.data['viewed_count'], 1)
        self.assertEqual(ComicView.objects.filter(comic=self.comic).count(), 1)
