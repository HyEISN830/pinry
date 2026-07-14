import time

from django.conf import settings
from django.core.files.uploadhandler import TemporaryFileUploadHandler


class ThrottledTemporaryFileUploadHandler(TemporaryFileUploadHandler):
    """Persist uploads to disk while limiting the aggregate request rate."""

    def __init__(self, request=None):
        super(ThrottledTemporaryFileUploadHandler, self).__init__(request)
        self.started_at = None
        self.received_bytes = 0

    def new_file(self, *args, **kwargs):
        if self.started_at is None:
            self.started_at = time.monotonic()
        return super(ThrottledTemporaryFileUploadHandler, self).new_file(
            *args, **kwargs
        )

    def receive_data_chunk(self, raw_data, start):
        if self.started_at is None:
            self.started_at = time.monotonic()
        self.received_bytes += len(raw_data)
        bytes_per_second = getattr(
            settings,
            'IMAGE_UPLOAD_THROTTLE_BYTES_PER_SECOND',
            1024 * 1024,
        )
        if bytes_per_second > 0:
            expected_elapsed = float(self.received_bytes) / bytes_per_second
            remaining = expected_elapsed - (time.monotonic() - self.started_at)
            if remaining > 0:
                time.sleep(remaining)
        return super(ThrottledTemporaryFileUploadHandler, self).receive_data_chunk(
            raw_data, start
        )
