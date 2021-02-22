from django.db import models
from apps.core.models import SignatureModel


class Enrolment(SignatureModel):
    qa = models.ForeignKey('programme.QA', models.DO_NOTHING, db_column='qa', blank=True, null=True)
    module = models.ForeignKey('module.Module', models.DO_NOTHING, db_column='module', related_name='enrolments')
    status = models.ForeignKey('EnrolmentStatus', models.DO_NOTHING, db_column='status')
    result = models.ForeignKey('EnrolmentResult', models.DO_NOTHING, db_column='result', default=7)
    points_awarded = models.IntegerField(blank=True, null=True)
    provenance = models.IntegerField(blank=True, null=True)
    provenance_details = models.CharField(max_length=128, blank=True, null=True)
    no_image_consent = models.BooleanField(blank=True, null=True)
    mark = models.IntegerField(blank=True, null=True)
    transcript_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'enrolment'

    def get_absolute_url(self):
        return '#'

    def student(self):
        return self.qa.student


class EnrolmentResult(SignatureModel):
    id = models.CharField(primary_key=True, max_length=4)
    description = models.CharField(max_length=128, blank=True, null=True)
    is_active = models.BooleanField()
    display_order = models.IntegerField(blank=True, null=True)
    hesa_code = models.CharField(max_length=1, blank=True, null=True)
    allow_certificate = models.BooleanField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'enrolment_result'


class EnrolmentStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64, blank=True, null=True)
    takes_place = models.BooleanField()
    is_debtor = models.BooleanField()
    on_hesa_return = models.BooleanField()

    class Meta:
        # managed = False
        db_table = 'enrolment_status'


class Catering(SignatureModel):
    fee = models.ForeignKey('module.Fee', models.DO_NOTHING, db_column='fee', related_name='catering')
    enrolment = models.ForeignKey('Enrolment', models.DO_NOTHING, db_column='enrolment', related_name='catering')

    class Meta:
        # managed = False
        db_table = 'catering'
