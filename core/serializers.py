from django.conf import settings
from django.db import transaction
from django.db.models import Prefetch, Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from taggit.models import Tag

from core.models import Image, Board, Comic, ComicPage
from core.models import Pin
from django_images.models import Thumbnail
from users.serializers import UserSerializer
from users.models import User


def filter_private_pin(request, query):
    if request.user.is_authenticated:
        query = query.exclude(~Q(submitter=request.user), private=True)
    else:
        query = query.exclude(private=True)
    visible_boards = filter_private_board(request, Board.objects.all())
    return query.select_related(
        'image',
        'submitter',
        'submitter__pinry_profile',
    ).prefetch_related(
        Prefetch('pins', queryset=visible_boards, to_attr='visible_boards'),
    )


def filter_private_board(request, query):
    if request.user.is_authenticated:
        query = query.exclude(~Q(submitter=request.user), private=True)
    else:
        query = query.exclude(private=True)
    return query


def filter_private_comic(request, query):
    if request.user.is_authenticated:
        query = query.exclude(~Q(submitter=request.user), private=True)
    else:
        query = query.exclude(private=True)
    return query.select_related(
        'submitter',
        'submitter__pinry_profile',
    ).prefetch_related(
        'pages',
        'pages__image',
        'pages__image__thumbnail_set',
    )


class ThumbnailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Thumbnail
        fields = (
            "image",
            "width",
            "height",
        )


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = (
            "id",
            "image",
            "width",
            "height",
            "standard",
            "thumbnail",
            "square",
        )
        extra_kwargs = {
            "width": {"read_only": True},
            "height": {"read_only": True},
        }

    standard = ThumbnailSerializer(read_only=True)
    thumbnail = ThumbnailSerializer(read_only=True)
    square = ThumbnailSerializer(read_only=True)

    def create(self, validated_data):
        image = super(ImageSerializer, self).create(validated_data)
        Thumbnail.objects.get_or_create_at_sizes(image, settings.IMAGE_SIZES.keys())
        return image


class TagSerializer(serializers.SlugRelatedField):
    class Meta:
        model = Tag
        fields = ("name",)

    queryset = Tag.objects.all()

    def __init__(self, **kwargs):
        super(TagSerializer, self).__init__(
            slug_field="name",
            **kwargs
        )

    def to_internal_value(self, data):
        obj, _ = self.get_queryset().get_or_create(
            defaults={self.slug_field: data, "slug": data},
            **{self.slug_field: data}
        )
        return obj


class PinBoardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Board
        fields = (
            settings.DRF_URL_FIELD_NAME,
            'id',
            'name',
            'private',
        )


class PinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pin
        fields = (
            settings.DRF_URL_FIELD_NAME,
            "private",
            "id",
            "submitter",
            "url",
            "description",
            "referer",
            "image",
            "image_by_id",
            "tags",
            "boards",
        )

    submitter = UserSerializer(read_only=True)
    tags = TagSerializer(
        many=True,
        source="tag_list",
        required=False,
    )
    image = ImageSerializer(required=False, read_only=True)
    image_by_id = serializers.PrimaryKeyRelatedField(
        queryset=Image.objects.all(),
        write_only=True,
        required=False,
    )
    boards = serializers.SerializerMethodField(read_only=True)

    def get_boards(self, instance):
        boards = getattr(instance, 'visible_boards', None)
        if boards is None:
            request = self.context['request']
            boards = filter_private_board(request, instance.pins.all())
        return PinBoardSerializer(boards, many=True, context=self.context).data

    def create(self, validated_data):
        if 'url' not in validated_data and\
                'image_by_id' not in validated_data:
            raise ValidationError(
                detail={
                    "url-or-image": "Either url or image_by_id is required."
                },
            )

        submitter = self.context['request'].user
        if 'url' in validated_data and validated_data['url']:
            url = validated_data['url']
            image = Image.objects.create_for_url(
                url,
                validated_data.get('referer', url),
            )
            if not image:
                raise ValidationError({"url": "invalid image content"})
        else:
            image = validated_data.pop("image_by_id")
        tags = validated_data.pop('tag_list', [])
        pin = Pin.objects.create(submitter=submitter, image=image, **validated_data)
        if tags:
            pin.tags.set(*tags)
        return pin

    def update(self, instance, validated_data):
        tags = validated_data.pop('tag_list', None)
        if tags:
            instance.tags.set(*tags)
        else:
            instance.tags.set()
        # change for image-id or image is not allowed
        validated_data.pop('image_by_id', None)
        return super(PinSerializer, self).update(instance, validated_data)


class PinIdListField(serializers.ListField):
    child = serializers.IntegerField(
        min_value=1
    )


class ComicPageAddSerializer(serializers.Serializer):
    image_by_id = serializers.PrimaryKeyRelatedField(
        queryset=Image.objects.all(),
    )
    order = serializers.IntegerField(min_value=1, required=False)
    caption = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
    )


class ComicPageMoveSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)
    order = serializers.IntegerField(min_value=1)


class ComicPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComicPage
        fields = (
            'id',
            'order',
            'caption',
            'image',
        )

    image = ImageSerializer(read_only=True)


class ComicSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comic
        fields = (
            settings.DRF_URL_FIELD_NAME,
            'id',
            'title',
            'description',
            'private',
            'published',
            'submitter',
            'total_pages',
            'cover',
            'pages',
            'pages_to_add',
            'pages_to_remove',
            'pages_to_reorder',
        )
        read_only_fields = ('submitter', 'published')

    submitter = UserSerializer(read_only=True)
    total_pages = serializers.SerializerMethodField(read_only=True)
    cover = serializers.SerializerMethodField(read_only=True)
    pages = ComicPageSerializer(many=True, read_only=True)
    pages_to_add = ComicPageAddSerializer(
        many=True,
        write_only=True,
        required=False,
    )
    pages_to_remove = PinIdListField(
        max_length=50,
        write_only=True,
        required=False,
        allow_empty=False,
    )
    pages_to_reorder = ComicPageMoveSerializer(
        many=True,
        write_only=True,
        required=False,
    )

    def get_total_pages(self, instance):
        return instance.pages.count()

    def get_cover(self, instance):
        page = instance.pages.order_by('order', 'id').first()
        if page is None:
            return None
        return ComicPageSerializer(page, context=self.context).data

    @staticmethod
    def _normalize_orders(comic, ordered_pages=None):
        if ordered_pages is None:
            ordered_pages = list(comic.pages.order_by('order', 'id'))
        with transaction.atomic():
            for index, page in enumerate(ordered_pages, start=10001):
                page.order = index
                page.save(update_fields=['order'])
            for index, page in enumerate(ordered_pages, start=1):
                page.order = index
                page.save(update_fields=['order'])

    def _add_page(self, comic, image, order=None, caption=None):
        pages = list(comic.pages.order_by('order', 'id'))
        if order is None:
            order = len(pages) + 1
        order = min(max(order, 1), len(pages) + 1)
        page = ComicPage(
            comic=comic,
            image=image,
            order=order,
            caption=caption,
        )
        pages.insert(order - 1, page)
        with transaction.atomic():
            for index, current_page in enumerate(pages, start=10001):
                if current_page.id is None:
                    continue
                current_page.order = index
                current_page.save(update_fields=['order'])
            for index, current_page in enumerate(pages, start=1):
                current_page.order = index
                current_page.comic = comic
                current_page.save()

    def _remove_pages(self, comic, page_ids):
        comic.pages.filter(id__in=page_ids).delete()
        self._normalize_orders(comic)

    def _reorder_pages(self, comic, move_items):
        pages = list(comic.pages.order_by('order', 'id'))
        for move_item in move_items:
            page_id = move_item['id']
            matched = [page for page in pages if page.id == page_id]
            if not matched:
                continue
            page = matched[0]
            pages.remove(page)
            new_index = min(max(move_item['order'], 1), len(pages) + 1) - 1
            pages.insert(new_index, page)
        self._normalize_orders(comic, pages)

    def create(self, validated_data):
        pages_to_add = validated_data.pop('pages_to_add', [])
        validated_data.pop('pages_to_remove', None)
        validated_data.pop('pages_to_reorder', None)
        validated_data['submitter'] = self.context['request'].user
        comic = super(ComicSerializer, self).create(validated_data)
        for page_data in pages_to_add:
            self._add_page(
                comic,
                page_data['image_by_id'],
                page_data.get('order'),
                page_data.get('caption'),
            )
        return comic

    def update(self, instance, validated_data):
        pages_to_add = validated_data.pop('pages_to_add', [])
        pages_to_remove = validated_data.pop('pages_to_remove', [])
        pages_to_reorder = validated_data.pop('pages_to_reorder', [])
        instance = super(ComicSerializer, self).update(instance, validated_data)
        if pages_to_remove:
            self._remove_pages(instance, pages_to_remove)
        if pages_to_reorder:
            self._reorder_pages(instance, pages_to_reorder)
        for page_data in pages_to_add:
            self._add_page(
                instance,
                page_data['image_by_id'],
                page_data.get('order'),
                page_data.get('caption'),
            )
        return instance


class BoardAutoCompleteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Board
        fields = (
            settings.DRF_URL_FIELD_NAME,
            'id',
            'name',
        )


class BoardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Board
        fields = (
            settings.DRF_URL_FIELD_NAME,
            "id",
            "name",
            "private",
            "total_pins",
            "cover",
            "published",
            "submitter",
            "pins_to_add",
            "pins_to_remove",
        )
        read_only_fields = ('submitter', 'published')
        extra_kwargs = {
            'submitter': {"view_name": "users:user-detail"},
        }

    submitter = UserSerializer(read_only=True)
    total_pins = serializers.SerializerMethodField(
        read_only=True,
    )
    cover = serializers.SerializerMethodField(
        read_only=True,
    )
    pins_to_add = PinIdListField(
        max_length=10,
        write_only=True,
        required=False,
        allow_empty=False,
        help_text="only patch method works for this field",
    )
    pins_to_remove = PinIdListField(
        max_length=10,
        write_only=True,
        required=False,
        allow_empty=False,
        help_text="only patch method works for this field"
    )

    def get_total_pins(self, instance):
        query = instance.pins.all()
        request = self.context['request']
        query = filter_private_pin(request, query)
        return query.count()

    def get_cover(self, instance: Board) -> dict or None:
        pin = instance.pins.first()
        if pin is None:
            return None
        return PinSerializer(pin, context=self.context).data

    @staticmethod
    def _get_list(pins_id, submitter: User):
        pins = Pin.objects.filter(id__in=pins_id)
        valid_pins = []
        for pin in pins:
            if pin.private and pin.submitter != submitter:
                continue
            valid_pins.append(pin)
        return valid_pins

    def update(self, instance: Board, validated_data):
        pins_to_add = validated_data.pop("pins_to_add", [])
        pins_to_remove = validated_data.pop("pins_to_remove", [])
        board = Board.objects.filter(
            submitter=instance.submitter,
            name=validated_data.get('name', None)
        ).first()
        if board and board.id != instance.id:
            raise ValidationError(
                detail={'name': "Board with this name already exists"}
            )
        instance = super(BoardSerializer, self).update(instance, validated_data)
        changed = False
        if pins_to_add:
            changed = True
            for pin in self._get_list(pins_to_add, instance.submitter):
                instance.pins.add(pin)
        if pins_to_remove:
            changed = True
            for pin in self._get_list(pins_to_remove, instance.submitter):
                instance.pins.remove(pin)
        if changed:
            instance.save()
        return instance

    def create(self, validated_data):
        validated_data.pop('pins_to_remove', None)
        validated_data.pop('pins_to_add', None)
        user = self.context['request'].user
        if Board.objects.filter(name=validated_data['name'], submitter=user).exists():
            raise ValidationError(
                detail={"name": "board with this name already exists."}
            )
        validated_data['submitter'] = user
        return super(BoardSerializer, self).create(validated_data)


class TagAutoCompleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('name', )
