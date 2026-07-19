import mimetypes
import time

from django.conf import settings
from django.db import IntegrityError
from django.db.models import Count, Exists, OuterRef, Q
from django.http import Http404, StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import viewsets, mixins, routers
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import GenericViewSet
from taggit.models import Tag

from core import serializers as api
from core.likes import (
    like_actor_key,
    like_actor_keys,
    like_ip_hash,
    view_actor_key,
    view_actor_keys,
    view_ip_hash,
)
from core.models import (
    Image,
    Pin,
    Board,
    Comic,
    PinLike,
    ComicLike,
    PinView,
    ComicView,
)
from core.permissions import IsOwnerOrReadOnly, OwnerOnlyIfPrivate
from core.throttles import (
    LikeDailyRateThrottle,
    LikeMinuteRateThrottle,
    ViewDailyRateThrottle,
    ViewMinuteRateThrottle,
)
from core.upload_views import ChunkedUploadViewSet
from core.serializers import (
    filter_private_pin,
    filter_private_board,
    filter_private_comic,
)


def annotate_like_state(query, like_model, object_field, request):
    like_filter = {
        '{}_id'.format(object_field): OuterRef('pk'),
        'actor_key__in': like_actor_keys(request),
    }
    return query.annotate(
        likes_count=Count('likes', distinct=True),
        viewer_liked=Exists(like_model.objects.filter(**like_filter)),
        viewed_count=Count('views', distinct=True),
        viewer_viewed=Exists(
            {
                'pin': PinView,
                'comic': ComicView,
            }[object_field].objects.filter(
                **{
                    '{}_id'.format(object_field): OuterRef('pk'),
                    'actor_key__in': view_actor_keys(request),
                },
            ),
        ),
    )


def toggle_like(request, obj, like_model, object_field):
    actor_key = like_actor_key(request)
    filters = {
        object_field: obj,
        'actor_key': actor_key,
    }
    existing_likes = like_model.objects.filter(
        **{
            object_field: obj,
            'actor_key__in': like_actor_keys(request),
        }
    )
    if existing_likes.exists():
        existing_likes.delete()
        liked = False
    else:
        defaults = {
            'ip_hash': like_ip_hash(request),
        }
        if request.user.is_authenticated:
            defaults['user'] = request.user
        try:
            _, created = like_model.objects.get_or_create(
                defaults=defaults,
                **filters
            )
        except IntegrityError:
            created = False
        liked = True if created else like_model.objects.filter(**filters).exists()
    count = obj.likes.count()
    return Response(
        {
            'liked': liked,
            'viewer_liked': liked,
            'likes_count': count,
        },
    )


def record_view(request, obj, view_model, object_field):
    """Record one view per actor, matching the like identity de-dup rules."""
    actor_key = view_actor_key(request)
    filters = {
        object_field: obj,
        'actor_key': actor_key,
    }
    existing_views = view_model.objects.filter(
        **{
            object_field: obj,
            'actor_key__in': view_actor_keys(request),
        },
    )
    viewed = existing_views.exists()
    if not viewed:
        defaults = {
            'ip_hash': view_ip_hash(request),
        }
        if request.user.is_authenticated:
            defaults['user'] = request.user
        try:
            _, created = view_model.objects.get_or_create(
                defaults=defaults,
                **filters
            )
        except IntegrityError:
            created = False
        # A concurrent request may win the unique constraint with the same
        # canonical actor key.  Re-check all compatible keys so that race
        # handling remains idempotent and never reports a false negative.
        viewed = bool(created) or view_model.objects.filter(
            **{
                object_field: obj,
                'actor_key__in': view_actor_keys(request),
            },
        ).exists()

    count = view_model.objects.filter(**{object_field: obj}).count()
    return Response(
        {
            'viewed': viewed,
            'viewer_viewed': viewed,
            'viewed_count': count,
        },
    )


class ImageViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = Image.objects.all()
    serializer_class = api.ImageSerializer

    def create(self, request, *args, **kwargs):
        return super(ImageViewSet, self).create(request, *args, **kwargs)

    @staticmethod
    def user_can_view_image(request, image):
        pins = image.pin.all()
        comics = image.comic_pages.select_related(
            'comic',
        )
        if request.user.is_authenticated:
            can_view_pin = pins.filter(
                Q(private=False) | Q(submitter=request.user)
            ).exists()
            can_view_comic = comics.filter(
                Q(comic__private=False) | Q(comic__submitter=request.user)
            ).exists()
            return can_view_pin or can_view_comic
        return (
            pins.filter(private=False).exists()
            or comics.filter(comic__private=False).exists()
        )

    @staticmethod
    def throttled_chunks(image_file, bytes_per_second):
        chunk_size = 64 * 1024
        with image_file.open('rb') as stream:
            while True:
                chunk = stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk
                time.sleep(len(chunk) / bytes_per_second)

    @action(detail=True, methods=['get'], url_path='original')
    def original(self, request, pk=None):
        image = self.get_object()
        if not self.user_can_view_image(request, image):
            raise Http404()

        image_file = image.image
        content_type, _ = mimetypes.guess_type(image_file.name)
        response = StreamingHttpResponse(
            self.throttled_chunks(
                image_file,
                settings.IMAGE_PREVIEW_THROTTLE_BYTES_PER_SECOND,
            ),
            content_type=content_type or 'application/octet-stream',
        )
        response['Content-Length'] = image_file.size
        response['Content-Disposition'] = 'inline'
        return response


class PinViewSet(viewsets.ModelViewSet):
    serializer_class = api.PinSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ("submitter__username", 'tags__name', "pins__id")
    ordering_fields = ('-id', )
    ordering = ('-id', )
    permission_classes = [IsOwnerOrReadOnly("submitter"), OwnerOnlyIfPrivate("submitter")]

    def get_queryset(self):
        query = Pin.objects.all()
        request = self.request
        return annotate_like_state(
            filter_private_pin(request, query),
            PinLike,
            'pin',
            request,
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[OwnerOnlyIfPrivate("submitter")],
        throttle_classes=[LikeMinuteRateThrottle, LikeDailyRateThrottle],
    )
    def like(self, request, pk=None):
        return toggle_like(request, self.get_object(), PinLike, 'pin')

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[OwnerOnlyIfPrivate("submitter")],
        throttle_classes=[ViewMinuteRateThrottle, ViewDailyRateThrottle],
    )
    def viewed(self, request, pk=None):
        return record_view(request, self.get_object(), PinView, 'pin')


class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = api.BoardSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ("name", )
    filter_fields = ("submitter__username", )
    ordering_fields = ('-id', )
    ordering = ('-id', )
    permission_classes = [IsOwnerOrReadOnly("submitter"), OwnerOnlyIfPrivate("submitter")]

    def get_queryset(self):
        return filter_private_board(self.request, Board.objects.all())


class ComicViewSet(viewsets.ModelViewSet):
    serializer_class = api.ComicSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ("title", "description", "tags__name")
    filter_fields = ("submitter__username", "tags__name")
    ordering_fields = ('-id', )
    ordering = ('-id', )
    permission_classes = [IsOwnerOrReadOnly("submitter"), OwnerOnlyIfPrivate("submitter")]

    def get_queryset(self):
        return annotate_like_state(
            filter_private_comic(self.request, Comic.objects.all()),
            ComicLike,
            'comic',
            self.request,
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[OwnerOnlyIfPrivate("submitter")],
        throttle_classes=[LikeMinuteRateThrottle, LikeDailyRateThrottle],
    )
    def like(self, request, pk=None):
        return toggle_like(request, self.get_object(), ComicLike, 'comic')

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[OwnerOnlyIfPrivate("submitter")],
        throttle_classes=[ViewMinuteRateThrottle, ViewDailyRateThrottle],
    )
    def viewed(self, request, pk=None):
        return record_view(request, self.get_object(), ComicView, 'comic')


class BoardAutoCompleteViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = api.BoardAutoCompleteSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = ("submitter__username", )
    ordering_fields = ('-id', )
    ordering = ('-id', )
    pagination_class = None
    permission_classes = [OwnerOnlyIfPrivate("submitter"), ]

    def get_queryset(self):
        return filter_private_board(self.request, Board.objects.all())


class TagAutoCompleteViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = api.TagAutoCompleteSerializer
    pagination_class = None

    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super(TagAutoCompleteViewSet, self).list(
            request,
            *args,
            **kwargs
        )


class AggregateSearchViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    pagination_class = None

    @staticmethod
    def parse_positive_int(value, default, maximum):
        try:
            number = int(value)
        except (TypeError, ValueError):
            return default
        return min(max(number, 0), maximum)

    def limited_results(self, query, serializer_class, offset, limit):
        items = list(query[offset:offset + limit + 1])
        has_next = len(items) > limit
        results = items[:limit]
        serializer = serializer_class(
            results,
            many=True,
            context={'request': self.request},
        )
        return {
            'results': serializer.data,
            'has_next': has_next,
            'next_offset': offset + len(results),
        }

    def empty_bucket(self, offset):
        return {
            'results': [],
            'has_next': False,
            'next_offset': offset,
        }

    def tag_results(self, query_text, offset, limit):
        query = Tag.objects.filter(
            name__icontains=query_text,
        ).order_by('name')
        items = list(query[offset:offset + limit + 1])
        has_next = len(items) > limit
        results = items[:limit]
        return {
            'results': [{'name': tag.name} for tag in results],
            'has_next': has_next,
            'next_offset': offset + len(results),
        }

    def list(self, request, *args, **kwargs):
        query_text = (request.query_params.get('q') or '').strip()
        query_text = query_text[:80]
        result_type = request.query_params.get('type') or 'all'
        allowed_types = ('all', 'pin', 'board', 'comic', 'tag')
        if result_type not in allowed_types:
            result_type = 'all'
        limit = self.parse_positive_int(
            request.query_params.get('limit'),
            8,
            18,
        )
        offsets = {
            'pins': self.parse_positive_int(
                request.query_params.get('pin_offset'),
                0,
                5000,
            ),
            'boards': self.parse_positive_int(
                request.query_params.get('board_offset'),
                0,
                5000,
            ),
            'comics': self.parse_positive_int(
                request.query_params.get('comic_offset'),
                0,
                5000,
            ),
            'tags': self.parse_positive_int(
                request.query_params.get('tag_offset'),
                0,
                5000,
            ),
        }
        response = {
            'query': query_text,
            'type': result_type,
            'limit': limit,
            'pins': self.empty_bucket(offsets['pins']),
            'boards': self.empty_bucket(offsets['boards']),
            'comics': self.empty_bucket(offsets['comics']),
            'tags': self.empty_bucket(offsets['tags']),
        }
        if not query_text:
            return Response(response)

        if result_type in ('all', 'pin'):
            pins = filter_private_pin(
                request,
                Pin.objects.filter(
                    Q(description__icontains=query_text)
                    | Q(tags__name__icontains=query_text),
                ).distinct().order_by('-id'),
            )
            response['pins'] = self.limited_results(
                annotate_like_state(pins, PinLike, 'pin', request),
                api.PinSerializer,
                offsets['pins'],
                limit,
            )
        if result_type in ('all', 'board'):
            boards = filter_private_board(
                request,
                Board.objects.filter(
                    name__icontains=query_text,
                ).distinct().order_by('-id'),
            )
            response['boards'] = self.limited_results(
                boards,
                api.BoardSerializer,
                offsets['boards'],
                limit,
            )
        if result_type in ('all', 'comic'):
            comics = filter_private_comic(
                request,
                Comic.objects.filter(
                    Q(title__icontains=query_text)
                    | Q(description__icontains=query_text)
                    | Q(tags__name__icontains=query_text),
                ).distinct().order_by('-id'),
            )
            response['comics'] = self.limited_results(
                annotate_like_state(comics, ComicLike, 'comic', request),
                api.ComicSerializer,
                offsets['comics'],
                limit,
            )
        if result_type in ('all', 'tag'):
            response['tags'] = self.tag_results(
                query_text,
                offsets['tags'],
                limit,
            )
        return Response(response)


drf_router = routers.DefaultRouter()
drf_router.register(r'pins', PinViewSet, basename="pin")
drf_router.register(r'images', ImageViewSet)
drf_router.register(r'uploads', ChunkedUploadViewSet, basename='upload')
drf_router.register(r'boards', BoardViewSet, basename="board")
drf_router.register(r'comics', ComicViewSet, basename="comic")
drf_router.register(r'tags-auto-complete', TagAutoCompleteViewSet)
drf_router.register(r'boards-auto-complete', BoardAutoCompleteViewSet, basename="board")
drf_router.register(r'search', AggregateSearchViewSet, basename="search")
