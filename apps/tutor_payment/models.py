from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from django.db import models, transaction

HOLIDAY_RATE = Decimal(0.1207 / 1.1207)
# Constants used as defaults.  If used more extensively, we may need to use enums
RAISED_STATUS = 1


class TutorFee(models.Model):
    tutor_module = models.ForeignKey(
        'tutor.TutorModule',
        models.DO_NOTHING,
        db_column='tutor_module',
        related_name='payments',
        related_query_name='payment',
    )
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    type = models.ForeignKey('TutorFeeType', models.DO_NOTHING, db_column='type', limit_choices_to={'is_active': True})
    pay_after = models.DateField(blank=True, null=True)
    status = models.ForeignKey('TutorFeeStatus', models.DO_NOTHING, db_column='status', default=RAISED_STATUS)
    details = models.CharField(max_length=500, blank=True, null=True)
    batch = models.PositiveIntegerField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    hours_worked = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    weeks = models.IntegerField(blank=True, null=True)
    approver = models.CharField(max_length=32)

    raised_by = models.CharField(max_length=50, editable=False)
    raised_on = models.DateTimeField(editable=False, auto_now_add=True)
    approved_by = models.CharField(max_length=50, blank=True, null=True, editable=False)
    approved_on = models.DateTimeField(blank=True, null=True, editable=False)
    transferred_by = models.CharField(max_length=50, blank=True, null=True, editable=False)
    transferred_on = models.DateTimeField(blank=True, null=True, editable=False)

    class Meta:
        # managed = False
        db_table = 'tutor_fee'

    @classmethod
    @transaction.atomic()
    def create_with_holiday(
        cls,
        tutor_module,
        amount,
        fee_type_id,
        details,
        hourly_rate,
        weeks,
        approver,
        raised_by,
        pay_date: date = None,
        holiday_date: date = None,
    ):
        """
        Raises a fee while separating out the holiday portion to a selected month
        The holiday payment date can be specified.  If not, it gets the last day of the module's end month.
        """
        if not holiday_date:
            # Get the last day of the last month of the module
            holiday_date = (
                date(tutor_module.module.start_date.year, tutor_module.module.end_date.month, 1)
                + relativedelta(months=1)
                - relativedelta(days=1)
            )

        holiday_amount = HOLIDAY_RATE * amount
        net_amount = amount - holiday_amount

        TutorFee.objects.create(
            tutor_module=tutor_module,
            amount=net_amount,
            type_id=fee_type_id,
            pay_after=pay_date,
            details=details,
            approver=approver,
            hourly_rate=hourly_rate,
            hours_worked=net_amount / hourly_rate,
            weeks=weeks,
            raised_by=raised_by,
        )

        # Holiday pay - last month
        TutorFee.objects.create(
            tutor_module=tutor_module,
            amount=holiday_amount,
            type_id=12,  # Holiday, todo choices
            pay_after=holiday_date,  # Last payment date
            details=f'{details} (holiday)',
            approver=approver,
            hourly_rate=hourly_rate,
            hours_worked=holiday_amount / hourly_rate,
            weeks=1,  # Not split across the month
            raised_by=raised_by,
        )


class TutorFeeRateQuerySet(models.QuerySet):
    def lookup(self, tag) -> Decimal:
        """Concise way of getting a fee_rate from a tag
        e.g. `marking_rate = TutorFeeRate.objects.lookup('marking')
        """
        return self.filter(tag=tag).first().amount


class TutorFeeRate(models.Model):
    tag = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    type = models.CharField(max_length=64, null=True)  # A label used for grouping
    description = models.CharField(max_length=128)

    objects = TutorFeeRateQuerySet.as_manager()

    class Meta:
        # managed = False
        db_table = 'tutor_fee_rate'

    def __str__(self):
        return f'£{self.amount:.2f} - {self.description}'


class TutorFeeStatus(models.Model):
    description = models.CharField(max_length=50, blank=True, null=True)
    paid = models.BooleanField()

    class Meta:
        # managed = False
        db_table = 'tutor_fee_status'

    def __str__(self):
        return self.description


class TutorFeeType(models.Model):
    description = models.CharField(max_length=64, blank=True, null=True)
    is_hourly = models.BooleanField()
    code = models.CharField(max_length=64, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'tutor_fee_type'

    def __str__(self):
        return self.description
