from django.contrib import admin

from . import models

admin.site.register(models.Programme)


@admin.register(models.ProgrammeModule)
class ProgrammeAdmin(admin.ModelAdmin):
    autocomplete_fields = ["module"]


admin.site.register(models.Qualification)
admin.site.register(models.StudyLocation)
