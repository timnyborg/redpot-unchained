from django.contrib import admin

from . import models

admin.site.register(models.Flag)
admin.site.register(models.System)
admin.site.register(models.MailingList)


@admin.register(models.Starter)
class StarterAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'lastname', 'job_title', 'email']
