import datetime
import uuid
from typing import Optional

from django.db import models
from django.db.models import Avg, Count, Q


class FeedbackQuerySet(models.QuerySet):
    def get_year_range(self, start_year: int, end_year: Optional[int] = None) -> models.QuerySet:
        end_year = end_year or start_year
        return self.filter(
            module__start_date__gt=datetime.date(start_year, 8, 31),
            module__start_date__lt=datetime.date(end_year + 1, 9, 1),
        )

    def statistics(self) -> dict:
        """Returns a standard set of statistics, used on multiple pages"""
        results = self.aggregate(
            teaching=Avg('rate_tutor'),
            content=Avg('rate_content'),
            facilities=Avg('rate_facilities'),
            admin=Avg('rate_admin'),
            catering=Avg('rate_refreshments'),
            accommodation=Avg('rate_accommodation'),
            average=Avg('avg_score'),
            sent=Count('id'),
            returned=Count('id', filter=Q(submitted__isnull=False)),
            high_scorers=Count('id', filter=Q(avg_score__gt=3.5)),
            total_scored=Count('id', filter=Q(avg_score__isnull=False)),
        )
        results['satisfied'] = None
        if results['total_scored']:
            results['satisfied'] = results['high_scorers'] / results['total_scored'] * 100
        return results


class Feedback(models.Model):
    module = models.ForeignKey('module.Module', models.DO_NOTHING, db_column='module', null=False)
    rate_tutor = models.IntegerField(blank=True, null=True)
    rate_content = models.IntegerField(blank=True, null=True)
    rate_admin = models.IntegerField(blank=True, null=True)
    rate_facilities = models.IntegerField(blank=True, null=True)
    rate_refreshments = models.IntegerField(blank=True, null=True)
    rate_accommodation = models.IntegerField(blank=True, null=True)
    your_name = models.CharField(blank=True, null=True, max_length=128)
    hash_id = models.CharField(default=uuid.uuid4, editable=False, unique=True, max_length=40)
    enrolment = models.IntegerField(blank=True, null=True)
    notified = models.DateTimeField(blank=True, null=True)
    submitted = models.DateTimeField(blank=True, null=True)
    avg_score = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    reminder = models.DateTimeField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'feedback'

    objects = FeedbackQuerySet.as_manager()


class FeedbackAdmin(models.Model):
    module = models.ForeignKey('module.Module', models.DO_NOTHING, db_column='module', null=False)
    updated = models.DateTimeField(blank=True, null=True)
    admin_comments = models.TextField(blank=True, null=True)
    person = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'feedback_admin'
