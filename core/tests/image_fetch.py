from datetime import timedelta

from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone

from core.models import Comic, ComicPage, ImageFetchJob, Pin
from core.serializers import ComicPageSerializer, ComicSerializer, PinSerializer
from pinry_plugins import runner

from .helpers import create_image, create_user


class ImageFetchJobModelTests(TestCase):
    def setUp(self):
        super(ImageFetchJobModelTests, self).setUp()
        self.user = create_user('image-fetch')
        self.image = create_image()
        self.pin = Pin.objects.create(
            submitter=self.user,
            image=self.image,
            url='https://example.com/pin',
            referer='https://example.com/',
        )

    def test_enqueue_for_pin_creates_pending_job(self):
        job = ImageFetchJob.enqueue_for_pin(
            self.pin,
            'https://example.com/image.jpg',
            'https://example.com/',
        )

        self.assertEqual(job.status, ImageFetchJob.STATUS_PENDING)
        self.assertEqual(job.source_url, 'https://example.com/image.jpg')
        self.assertEqual(job.referer, 'https://example.com/')
        self.assertEqual(job.pin, self.pin)

    def test_claim_next_marks_job_processing(self):
        ImageFetchJob.enqueue_for_pin(self.pin, 'https://example.com/image.jpg')

        job = ImageFetchJob.claim_next()

        self.assertEqual(job.status, ImageFetchJob.STATUS_PROCESSING)
        self.assertEqual(job.attempts, 1)
        self.assertIsNotNone(job.started)

    def test_reset_stale_processing_returns_job_to_pending(self):
        job = ImageFetchJob.enqueue_for_pin(self.pin, 'https://example.com/image.jpg')
        job.status = ImageFetchJob.STATUS_PROCESSING
        job.started = timezone.now() - timedelta(seconds=120)
        job.save(update_fields=['status', 'started'])

        reset_count = ImageFetchJob.reset_stale_processing(timeout_seconds=60)
        job.refresh_from_db()

        self.assertEqual(reset_count, 1)
        self.assertEqual(job.status, ImageFetchJob.STATUS_PENDING)
        self.assertIsNone(job.started)


class ImageFetchSerializerStatusTests(TestCase):
    def setUp(self):
        super(ImageFetchSerializerStatusTests, self).setUp()
        self.user = create_user('image-fetch-serializer')
        self.image = create_image()
        self.factory = RequestFactory()

    def _request(self):
        request = self.factory.get('/')
        request.user = self.user
        return request

    def test_pin_serializer_exposes_pending_image_fetch_fields(self):
        pin = Pin.objects.create(
            submitter=self.user,
            image=None,
            url='https://example.com/pin',
            referer='https://example.com/',
        )
        job = ImageFetchJob.enqueue_for_pin(
            pin,
            'https://example.com/image.jpg',
        )

        data = PinSerializer(pin, context={'request': self._request()}).data

        self.assertEqual(data['image_fetch_status'], ImageFetchJob.STATUS_PENDING)
        self.assertIsNone(data['image_fetch_error'])
        self.assertEqual(data['image_fetch_job_id'], job.id)

    def test_comic_page_serializer_exposes_failed_image_fetch_fields(self):
        comic = Comic.objects.create(
            submitter=self.user,
            title='Async comic',
            referer='https://example.com/',
        )
        page = ComicPage.objects.create(comic=comic, image=None, order=1)
        job = ImageFetchJob.enqueue_for_comic_page(
            page,
            'https://example.com/page.jpg',
        )
        job.status = ImageFetchJob.STATUS_FAILED
        job.error = 'download failed'
        job.save(update_fields=['status', 'error'])

        data = ComicPageSerializer(page, context={'request': self._request()}).data

        self.assertEqual(data['image_fetch_status'], ImageFetchJob.STATUS_FAILED)
        self.assertEqual(data['image_fetch_error'], 'download failed')
        self.assertEqual(data['image_fetch_job_id'], job.id)


class ImageFetchAsyncSerializerTests(TestCase):
    def setUp(self):
        super(ImageFetchAsyncSerializerTests, self).setUp()
        self.user = create_user('image-fetch-async')
        self.factory = RequestFactory()

    def _request(self):
        request = self.factory.post('/')
        request.user = self.user
        return request

    @override_settings(IMAGE_FETCH_ASYNC_ENABLED=True)
    def test_pin_serializer_enqueues_job_without_fetching_image(self):
        serializer = PinSerializer(
            data={
                'url': 'https://example.com/image.jpg',
                'referer': 'https://example.com/',
                'description': 'queued pin',
                'tags': [],
            },
            context={'request': self._request()},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        pin = serializer.save()

        self.assertIsNone(pin.image_id)
        self.assertEqual(pin.image_fetch_job.status, ImageFetchJob.STATUS_PENDING)
        self.assertEqual(
            pin.image_fetch_job.source_url,
            'https://example.com/image.jpg',
        )
    @override_settings(IMAGE_FETCH_ASYNC_ENABLED=True)
    def test_comic_serializer_enqueues_one_job_per_url_page(self):
        serializer = ComicSerializer(
            data={
                'title': 'Queued comic',
                'pages_to_add': [
                    {
                        'url': 'https://example.com/page-1.jpg',
                        'caption': 'page 1',
                    },
                    {
                        'url': 'https://example.com/page-2.jpg',
                        'caption': 'page 2',
                    },
                ],
                'tags': [],
            },
            context={'request': self._request()},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        comic = serializer.save()

        self.assertEqual(comic.pages.count(), 2)
        self.assertEqual(ImageFetchJob.objects.filter(comic_page__comic=comic).count(), 2)
        for page in comic.pages.all():
            self.assertIsNone(page.image_id)
            self.assertEqual(page.image_fetch_job.status, ImageFetchJob.STATUS_PENDING)


class PluginRunnerTests(TestCase):
    @override_settings(ENABLED_PLUGINS=[])
    def test_runner_loads_plugins_idempotently(self):
        runner._plugin_instances = None

        first = runner.get_plugin_instances()
        second = runner.get_plugin_instances()

        self.assertIs(first, second)
