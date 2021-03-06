from datetime import datetime
from typing import Optional

from django.db import models


class BannerQuerySet(models.QuerySet):
    def past(self) -> models.QuerySet:
        return self.filter(publish__lte=datetime.today())

    def current(self) -> Optional['Banner']:
        """Get the newest banner message for display"""
        return self.filter(publish__lte=datetime.today()).exclude(unpublish__lte=datetime.today()).first()


class Banner(models.Model):
    """A feature, update, or alert message which appears atop the home page.
    Todo: consider making banners appear atop every page, until dismissed (with a last-dismissed column on User?,
      or just an "Updates!" link on the topnav which is marked unread until accessed
    """

    class Types(models.IntegerChoices):
        NEW = 1, 'New feature'
        ALERT = 2, 'Alert'
        OTHER = 3, 'Other'

    message = models.CharField(max_length=200)
    type = models.IntegerField(choices=Types.choices)
    publish = models.DateField()
    unpublish = models.DateField(blank=True, null=True)
    description = models.TextField()

    objects = BannerQuerySet.as_manager()

    class Meta:
        db_table = 'banner'
        ordering = ['-publish']

    def __str__(self) -> str:
        return str(self.message)
