from django.contrib import admin

from . import models

admin.site.register(models.Programme)


@admin.register(models.QA)
class QAAdmin(admin.ModelAdmin):
    readonly_fields = ["student"]
    list_display = ['id', 'student', 'title', 'created_on', 'created_by', 'modified_on', 'modified_by']


@admin.register(models.ProgrammeModule)
class ProgrammeAdmin(admin.ModelAdmin):
    autocomplete_fields = ["module"]


admin.site.register(models.EntryQualification)
admin.site.register(models.Qualification)
admin.site.register(models.StudyLocation)
