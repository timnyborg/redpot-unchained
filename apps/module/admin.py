from django.contrib import admin

from .models import Module


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    search_fields = ["code", "title"]
    list_display = ('long_form',)
