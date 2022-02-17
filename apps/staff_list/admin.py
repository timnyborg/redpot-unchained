from django.contrib import admin

from . import models


@admin.register(models.ProgrammeStaff)
class ProgrammeStaffAdmin(admin.ModelAdmin):
    search_fields = ["programme__title", "staff__first_name", "staff__last_name"]
    list_display = ("programme", "get_staff", "role")

    @admin.display(ordering='staff__first_name', description='Staff member')
    def get_staff(self, obj) -> str:
        return obj.staff.get_full_name()
