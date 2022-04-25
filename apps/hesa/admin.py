from django.contrib import admin

from . import models


@admin.register(models.HECoSSubject)
class HECoSSubjectAdmin(admin.ModelAdmin):
    search_fields = ["id", "name", "cost_centre__description"]
    list_display = ["id", "name", "cost_centre"]


@admin.register(models.HESACostCentre)
class HESACostCentreAdmin(admin.ModelAdmin):
    search_fields = ["id", "description", "price_group"]
    list_display = ["id", "description", "price_group"]


@admin.register(models.ProgrammeHecosSubject)
class ProgrammeHecosSubjectAdmin(admin.ModelAdmin):
    search_fields = ["programme__title", "hecos_subject__name", "percentage"]
    list_display = ["programme", "hecos_subject", "percentage"]
