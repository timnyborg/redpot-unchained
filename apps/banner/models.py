from datetime import datetime

from django.db import models


class BannerQuerySet(models.QuerySet):
    def past(self) -> models.QuerySet:
        return self.filter(publish__lte=datetime.today())


class Banner(models.Model):
    """A feature, update, or alert message which appears atop the home page"""

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
