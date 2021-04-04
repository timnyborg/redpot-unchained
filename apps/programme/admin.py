from django.contrib import admin

from . import models

admin.site.register(models.Division)
admin.site.register(models.Portfolio)
admin.site.register(models.Programme)


@admin.register(models.ProgrammeModule)
class ProgrammeAdmin(admin.ModelAdmin):
    autocomplete_fields = ["module"]
