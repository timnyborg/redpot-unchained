from django.contrib import admin

from . import models


@admin.register(models.QualificationAim)
class QualificationAimAdmin(admin.ModelAdmin):
    readonly_fields = ["student"]
    list_display = ['id', 'student', 'title', 'created_on', 'created_by', 'modified_on', 'modified_by']


admin.site.register(models.EntryQualification)
