from decimal import Decimal

from django.db import models
from django.urls import reverse

from apps.core.models import SignatureModel
from apps.finance.models import Accounts

# Constants used as defaults.  If used more extensively, we may need to use enums
NOT_CODED_RESULT = 7


class Statuses(models.IntegerField):
    """Non-exhaustive list of statuses used in business logic"""

    CONFIRMED = 10
    PROVISIONAL = 20
    CONFIRMED_NON_CREDIT = 90


class EnrolmentQuerySet(models.QuerySet):
    def outstanding(self):
        """Enrolments with balance > 0"""
        return self.with_balance().filter(balance__gt=0)

    def with_balance(self):
        """Add an outstanding `balance` attribute to each row.
        If the ledger items are filtered in another way (e.g. connected to a given invoice),
        the balance will reflect that filtered set
        """
        return self.annotate(balance=models.Sum('ledger__amount', filter=models.Q(ledger__account=Accounts.DEBTOR)))


class Enrolment(SignatureModel):
    qa = models.ForeignKey(
        'qualification_aim.QualificationAim',
        models.DO_NOTHING,
        db_column='qa',
        related_name='enrolments',
        related_query_name='enrolment',
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

    objects = EnrolmentQuerySet.as_manager()

    class Meta:
        # managed = False
        db_table = 'enrolment'

    def get_absolute_url(self):
        return reverse('enrolment:view', args=[self.pk])

    def get_balance(self) -> Decimal:
        ledger_balance = self.ledger_set.debts().total()
        return ledger_balance or Decimal(0)


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

    def __str__(self):
        return str(self.description)


class EnrolmentStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64, blank=True, null=True)
    takes_place = models.BooleanField()
    is_debtor = models.BooleanField()
    on_hesa_return = models.BooleanField()

    class Meta:
        # managed = False
        db_table = 'enrolment_status'

    def __str__(self):
        return str(self.description)
