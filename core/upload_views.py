import math

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.chunked_uploads import (
    append_chunk,
    complete_upload,
    create_or_resume_upload,
    delete_upload_file,
    next_chunk_after_ms,
    reconcile_upload_file,
    reserve_chunk_bandwidth,
)
from core.models import ChunkedUpload
from core.serializers import ChunkedUploadSerializer


def upload_data(upload):
    return {
        'id': str(upload.id),
        'target': upload.target,
        'filename': upload.filename,
        'total_size': upload.total_size,
        'received_size': upload.received_size,
        'status': upload.status,
        'chunk_size': settings.CHUNKED_UPLOAD_CHUNK_SIZE,
    }


class ChunkedUploadViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    pagination_class = None
    serializer_class = ChunkedUploadSerializer

    def get_queryset(self):
        return ChunkedUpload.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        upload, created = create_or_resume_upload(
            request.user,
            request,
            request.data,
        )
        return Response(
            upload_data(upload),
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        upload = self.get_object()
        if upload.status == ChunkedUpload.STATUS_UPLOADING:
            upload = reconcile_upload_file(upload)
        return Response(upload_data(upload))

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            upload = get_object_or_404(
                self.get_queryset().select_for_update(),
                pk=kwargs.get('pk'),
            )
            if upload.status == ChunkedUpload.STATUS_PROCESSING:
                return Response(
                    {
                        'detail': (
                            'An upload being processed cannot be canceled.'
                        ),
                    },
                    status=status.HTTP_409_CONFLICT,
                )
            delete_upload_file(upload)
            upload.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['put'], url_path='chunk')
    def chunk(self, request, pk=None):
        try:
            offset = int(request.META.get('HTTP_X_UPLOAD_OFFSET', ''))
        except (TypeError, ValueError):
            raise ValidationError({'offset': 'X-Upload-Offset is required.'})
        try:
            content_length = int(request.META.get('HTTP_X_UPLOAD_LENGTH', ''))
        except (TypeError, ValueError):
            raise ValidationError({'chunk': 'X-Upload-Length is required.'})
        try:
            request_content_length = int(
                request.META.get('CONTENT_LENGTH', ''),
            )
        except (TypeError, ValueError):
            request_content_length = None
        if (
            request_content_length is not None
            and request_content_length != content_length
        ):
            raise ValidationError({
                'chunk': 'Chunk length does not match Content-Length.',
            })
        if (
            content_length <= 0
            or content_length > settings.CHUNKED_UPLOAD_CHUNK_SIZE
        ):
            raise ValidationError({
                'chunk': 'Invalid chunk size.',
            })
        with transaction.atomic():
            upload = get_object_or_404(
                self.get_queryset().select_for_update(),
                pk=pk,
            )
            upload = reconcile_upload_file(upload)
            if offset != upload.received_size:
                return Response(
                    upload_data(upload),
                    status=status.HTTP_409_CONFLICT,
                )
            wait_ms = reserve_chunk_bandwidth(upload, content_length)
            if wait_ms > 0:
                response = Response(
                    {
                        'detail': 'Upload rate limit reached.',
                        'retry_after_ms': wait_ms,
                        'received_size': upload.received_size,
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
                response['Retry-After'] = str(max(1, int(math.ceil(
                    wait_ms / 1000.0,
                ))))
                response['X-Retry-After-Ms'] = str(wait_ms)
                return response
            chunk = request.body
            if len(chunk) != content_length:
                raise ValidationError({'chunk': 'Incomplete chunk body.'})
            upload = append_chunk(upload, offset, chunk)
        data = upload_data(upload)
        data['next_chunk_after_ms'] = next_chunk_after_ms(len(chunk))
        return Response(data)

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        upload = self.get_object()
        result = complete_upload(upload, request)
        upload.refresh_from_db()
        data = upload_data(upload)
        if result is None:
            return Response(data, status=status.HTTP_202_ACCEPTED)
        data['result'] = result
        return Response(data)
