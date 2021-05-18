from django.db import models

from apps.core.models import SignatureModel

# Constants used as defaults.  If used more extensively, we may need to use enums
NOT_CODED_RESULT = 7


class Enrolment(SignatureModel):
    qa = models.ForeignKey(
        'programme.QA', models.DO_NOTHING, db_column='qa', related_name='enrolments', related_query_name='enrolment'
    )
    module = models.ForeignKey(
        'module.Module',
        models.DO_NOTHING,
        db_column='module',
        related_name='enrolments',
        related_query_name='enrolment',
    )
    status = models.ForeignKey('EnrolmentStatus', models.DO_NOTHING, db_column='status')
    result = models.ForeignKey(
        'EnrolmentResult',
        models.DO_NOTHING,
        db_column='result',
        limit_choices_to={'is_active': True},
        default=NOT_CODED_RESULT,
    )
    points_awarded = models.IntegerField(blank=True, null=True)
    mark = models.IntegerField(blank=True, null=True)
    transcript_date = models.DateTimeField(blank=True, null=True, editable=False)

    class Meta:
        # managed = False
        db_table = 'enrolment'

    def get_absolute_url(self):
        return '#'

    def student(self):
        return self.qa.student


class EnrolmentResult(SignatureModel):
    """
    `id` is a terrifying bit of backwards compatibility.
    The PK used to be HESA's 1-9 + A-C, but then values like '2.1' were added for special cases
    It should all be replaced with integers, but that will require a survey of its use in reporting
    """

    id = models.CharField(primary_key=True, max_length=4)
    description = models.CharField(max_length=128, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(blank=True, null=True)
    hesa_code = models.CharField(max_length=1)
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
