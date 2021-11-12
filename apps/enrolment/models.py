from decimal import Decimal

from django.db import models
from django.urls import reverse

from apps.core.models import SignatureModel
from apps.finance.models import Accounts


class Results(models.TextChoices):
    PASSED = '1'
    NOT_CODED = '7'


class Statuses(models.IntegerChoices):
    """Non-exhaustive list of statuses used in business logic"""

    CONFIRMED = 10
    CONFIRMED_RETROSPECTIVE_CREDIT = 11  # todo: consider ditching this retro. option
    PROVISIONAL = 20
    CONFIRMED_NON_CREDIT = 90


FOR_CREDIT_STATUSES = {Statuses.CONFIRMED, Statuses.CONFIRMED_RETROSPECTIVE_CREDIT}


class EnrolmentQuerySet(models.QuerySet):
    def outstanding(self) -> models.QuerySet:
        """Enrolments with balance > 0"""
        return self.with_balance().filter(balance__gt=0)

    def with_balance(self) -> models.QuerySet:
        """Add an outstanding `balance` attribute to each row.
        If the ledger items are filtered in another way (e.g. connected to a given invoice),
        the balance will reflect that filtered set
        """
        return self.annotate(balance=models.Sum('ledger__amount', filter=models.Q(ledger__account=Accounts.DEBTOR)))

    def transcript_printable(self) -> models.QuerySet:
        """Enrolments which can appear on a transcript (confirmed status, passed result, points awarded)"""
        return (
            self.filter(
                status_id__in=FOR_CREDIT_STATUSES,
                result_id=Results.PASSED,
                points_awarded__gt=0,
            )
            .exclude(module__start_date__isnull=True)  # Filter out very old incomplete module records
            .exclude(module__end_date__isnull=True)
        )


class Enrolment(SignatureModel):
    qa = models.ForeignKey(
        'qualification_aim.QualificationAim',
        models.PROTECT,
        db_column='qa',
        related_name='enrolments',
        related_query_name='enrolment',
        verbose_name='Qualification aim',
    )
    module = models.ForeignKey(
        'module.Module',
        models.PROTECT,
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
        default=Results.NOT_CODED,
    )
    points_awarded = models.IntegerField(blank=True, null=True)
    mark = models.IntegerField(blank=True, null=True)
    transcript_date = models.DateTimeField(blank=True, null=True, editable=False)

    objects = EnrolmentQuerySet.as_manager()

    class Meta:
        db_table = 'enrolment'
        permissions = [('edit_mark', "User can edit enrolments' marks")]

    def __str__(self) -> str:
        return f'{self.qa.student} on {self.module}'

    def get_absolute_url(self) -> str:
        return reverse('enrolment:view', args=[self.pk])

    def get_edit_url(self) -> str:
        return reverse('enrolment:edit', args=[self.pk])

    def get_delete_url(self) -> str:
        return reverse('enrolment:delete', args=[self.pk])

    def save(self, *args, **kwargs) -> None:
        # Update points awarded if student has 'Passed' and Status is 'Confirmed' or 'Confirmed - retrospective credit'
        self.points_awarded = (
            self.module.credit_points
            if self.result_id == Results.PASSED and self.status_id in FOR_CREDIT_STATUSES
            else 0
        )
        super().save(*args, **kwargs)

    def get_balance(self) -> Decimal:
        ledger_balance = self.ledger_set.debts().total()
        return ledger_balance or Decimal(0)

    # todo: implement as a column (take logic out of status, removing values 11 & 90)
    @property
    def for_credit(self) -> bool:
        return self.status_id in (10, 11)


class EnrolmentResult(SignatureModel):
    """
    `id` is a terrifying bit of backwards compatibility.
    The PK used to be HESA's 1-9 + A-C, but then values like '2.1' were added for special cases
    It should all be replaced with integers, but that will require a survey of its use in reporting
    """

    id = models.CharField(primary_key=True, max_length=4)
    description = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField()
    hesa_code = models.CharField(max_length=1)
    allow_certificate = models.BooleanField(default=False)

    class Meta:
        db_table = 'enrolment_result'
        ordering = ('display_order', 'id')

    def __str__(self):
        return str(self.description)


class EnrolmentStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64)
    takes_place = models.BooleanField()
    on_hesa_return = models.BooleanField()

    class Meta:
        db_table = 'enrolment_status'

    def __str__(self):
        return str(self.description)
