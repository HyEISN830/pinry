from django.contrib import admin

from .models import Pin, Board, Comic, ComicPage, PinLike, ComicLike


class PinAdmin(admin.ModelAdmin):
    pass


admin.site.register(Pin, PinAdmin)
admin.site.register(Board)
admin.site.register(Comic)
admin.site.register(ComicPage)
admin.site.register(PinLike)
admin.site.register(ComicLike)
