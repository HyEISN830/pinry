import signal
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import OperationalError

from core.models import ImageFetchJob


class Command(BaseCommand):
    help = 'Process queued image fetch jobs.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--once',
            action='store_true',
            help='Process available jobs once, then exit.',
        )
        parser.add_argument(
            '--idle-seconds',
            type=float,
            default=getattr(settings, 'IMAGE_FETCH_WORKER_IDLE_SECONDS', 5),
            help='Seconds to wait between empty queue polls.',
        )
        parser.add_argument(
            '--processing-timeout-seconds',
            type=int,
            default=getattr(
                settings,
                'IMAGE_FETCH_PROCESSING_TIMEOUT_SECONDS',
                900,
            ),
            help='Reset processing jobs older than this many seconds.',
        )
        parser.add_argument(
            '--db-lock-backoff-seconds',
            type=float,
            default=getattr(
                settings,
                'IMAGE_FETCH_DB_LOCK_BACKOFF_SECONDS',
                2,
            ),
            help='Seconds to wait after a database lock error.',
        )

    def handle(self, *args, **options):
        self.should_stop = False
        self._install_signal_handlers()
        reset_count = ImageFetchJob.reset_stale_processing(
            options['processing_timeout_seconds'],
        )
        if reset_count:
            self.stdout.write(
                'Reset {} stale image fetch job(s).'.format(reset_count),
            )

        while not self.should_stop:
            try:
                job = ImageFetchJob.claim_next()
                if job is None:
                    if options['once']:
                        break
                    self._sleep(options['idle_seconds'])
                    continue
                job.process()
            except OperationalError as exc:
                self.stderr.write(
                    'Database unavailable while processing image fetch job: {}'.format(exc),
                )
                self._sleep(options['db_lock_backoff_seconds'])

            if options['once']:
                continue

    def _install_signal_handlers(self):
        for signal_name in ('SIGTERM', 'SIGINT'):
            sig = getattr(signal, signal_name, None)
            if sig is None:
                continue
            signal.signal(sig, self._handle_shutdown_signal)

    def _handle_shutdown_signal(self, signum, frame):
        self.should_stop = True

    def _sleep(self, seconds):
        deadline = time.time() + max(seconds, 0)
        while not self.should_stop and time.time() < deadline:
            time.sleep(min(0.2, deadline - time.time()))
