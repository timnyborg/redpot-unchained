from django.contrib import admin

from django.contrib import admin
from .models import Programme, ProgrammeModule

admin.site.register(Programme)


@admin.register(ProgrammeModule)
class ProgrammeAdmin(admin.ModelAdmin):
    autocomplete_fields = ["module"]
