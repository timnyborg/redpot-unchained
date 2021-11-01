import uuid

from django.db import models


class Feedback(models.Model):
    module = models.ForeignKey('module.Module', models.DO_NOTHING, db_column='module', null=True)
    rate_tutor = models.IntegerField(blank=True, null=True)
    rate_content = models.IntegerField(blank=True, null=True)
    rate_admin = models.IntegerField(blank=True, null=True)
    rate_facilities = models.IntegerField(blank=True, null=True)
    rate_refreshments = models.IntegerField(blank=True, null=True)
    rate_accommodation = models.IntegerField(blank=True, null=True)
    your_name = models.TextField(blank=True, null=True)
    hash_id = models.CharField(default=uuid.uuid4, editable=False, unique=True, max_length=40)
    enrolment = models.IntegerField(blank=True, null=True)
    notified = models.DateTimeField(blank=True, null=True)
    submitted = models.DateTimeField(blank=True, null=True)
    avg_score = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    reminder = models.DateTimeField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'feedback'


class FeedbackAdmin(models.Model):
    module = models.ForeignKey('module.Module', models.DO_NOTHING, db_column='module', null=True)
    updated = models.DateTimeField(blank=True, null=True)
    admin_comments = models.TextField(blank=True, null=True)
    person = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'feedback_admin'
