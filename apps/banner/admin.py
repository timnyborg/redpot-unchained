from ckeditor.widgets import CKEditorWidget

from django.contrib import admin
from django.db.models import TextField

from . import models


@admin.register(models.Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['message', 'type', 'publish', 'unpublish']
    formfield_overrides = {TextField: {'widget': CKEditorWidget}}
