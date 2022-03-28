from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.urls import reverse
from django.utils.functional import cached_property

from apps.core.models import User

HOLIDAY_RATE = Decimal(0.1207 / 1.1207)


class Statuses(models.IntegerChoices):
    RAISED = 1, 'Raised'
    APPROVED = 2, 'Approved'
    TRANSFERRED = 3, 'Transferred'
    FAILED = 4, 'Failed'


class Types(models.IntegerChoices):
    # Non-exhaustive list
    ADMIN = 1
    TEACHING = 2
    EXAMINING = 4
    HOLIDAY_PAY = 12


class TutorPayment(models.Model):
    tutor_module = models.ForeignKey(
        'tutor.TutorModule',
        models.PROTECT,
        db_column='tutor_module',
        related_name='payments',
        related_query_name='payment',
    )
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    type = models.ForeignKey(
        'PaymentType',
        models.DO_NOTHING,
        db_column='type',
        limit_choices_to={'is_active': True},
    )
    pay_after = models.DateField(blank=True, null=True)
    status = models.ForeignKey('PaymentStatus', models.DO_NOTHING, db_column='status', default=Statuses.RAISED)
    details = models.TextField(max_length=500, blank=True, null=True)
    batch = models.PositiveIntegerField(blank=True, null=True, editable=False)
    hourly_rate = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    hours_worked = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    weeks = models.IntegerField()
    approver = models.ForeignKey(
        'core.User',
        on_delete=models.DO_NOTHING,
        db_column='approver',
        related_name='approver_payments',
        related_query_name='approver_payment',
        to_field='username',
    )
    raised_by = models.ForeignKey(
        'core.User',
        on_delete=models.DO_NOTHING,
        db_column='raised_by',  # todo: implement fk on legacy db, or move to an id fk
        related_name='tutor_payments',
        related_query_name='tutor_payment',
        to_field='username',
    )
    raised_on = models.DateTimeField(editable=False, default=datetime.now)
    approved_by = models.CharField(max_length=50, blank=True, null=True, editable=False)
    approved_on = models.DateTimeField(blank=True, null=True, editable=False)
    transferred_by = models.CharField(max_length=50, blank=True, null=True, editable=False)
    transferred_on = models.DateTimeField(blank=True, null=True, editable=False)

    class Meta:
        db_table = 'tutor_fee'
        permissions = [
            ('raise', 'Can raise tutor payments'),
            ('approve', 'Can approve tutor payments'),
            ('transfer', 'Can transfer tutor payments to central finance'),
        ]

    def save(self, *args, **kwargs):
        # Reverting a transferred record wipes related fields
        if self.status_id < Statuses.TRANSFERRED:
            self.batch = None
            self.transferred_by = None
            self.transferred_on = None
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse('tutor-payment:view', args=[self.pk])

    def get_edit_url(self) -> str:
        return reverse('tutor-payment:edit', args=[self.pk])

    def get_delete_url(self) -> str:
        return reverse('tutor-payment:delete', args=[self.pk])

    @classmethod
    @transaction.atomic()
    def create_with_holiday(
        cls,
        tutor_module,
        amount,
        payment_type_id,
        details,
        hourly_rate,
        weeks,
        approver,
        raised_by,
        pay_date: date = None,
        holiday_date: date = None,
    ):
        """
        Raises a payment while separating out the holiday portion to a selected month
        The holiday payment date can be specified.  If not, it gets the last day of the module's end month.
        """
        if not holiday_date:
            # Get the last day of the last month of the module
            holiday_date = date(
                tutor_module.module.start_date.year, tutor_module.module.end_date.month, 1
            ) + relativedelta(months=1)

        holiday_amount = HOLIDAY_RATE * amount
        net_amount = amount - holiday_amount

        TutorPayment.objects.create(
            tutor_module=tutor_module,
            amount=net_amount,
            type_id=payment_type_id,
            pay_after=pay_date,
            details=details,
            approver=approver,
            hourly_rate=hourly_rate,
            hours_worked=net_amount / hourly_rate,
            weeks=weeks,
            raised_by=raised_by,
        )

        # Holiday pay - last month
        TutorPayment.objects.create(
            tutor_module=tutor_module,
            amount=holiday_amount,
            type_id=Types.HOLIDAY_PAY,
            pay_after=holiday_date,  # Last payment date
            details=f'{details} (holiday)',
            approver=approver,
            hourly_rate=hourly_rate,
            hours_worked=holiday_amount / hourly_rate,
            weeks=1,  # Not split across the month
            raised_by=raised_by,
        )

    @cached_property
    def _approvable(self) -> dict:
        errors = []

        module = self.tutor_module.module
        tutor = self.tutor_module.tutor

        if not module.finance_code:
            errors.append('Module missing a finance code.')
        if not tutor.appointment_id:
            errors.append('Tutor missing an appointment ID.')
        if not tutor.employee_no:
            errors.append('Tutor missing an employee number.')
        if not tutor.rtw_type:
            # todo: consider more extensive rules re. end-dates
            errors.append('Tutor missing Right to Work data.')

        # Result and error messages
        return {
            'approvable': not errors,
            'errors': errors,
        }

    def approvable(self) -> bool:
        """Check that a payment and its associated records are complete"""
        return self._approvable['approvable']

    def approval_errors(self) -> list:
        """Return a list of error messages if a payment cannot be approved"""
        return self._approvable['errors']

    def clean(self):
        # Check that the total amount math works out.
        errors = {}
        if self.type_id and self.type.is_hourly:
            if not self.hours_worked:
                errors['hours_worked'] = 'Required'
            if not self.hourly_rate:
                errors['hourly_rate'] = 'Required'
            if not self.weeks:
                errors['weeks'] = 'Required'

            if (
                self.hours_worked
                and self.hourly_rate
                and abs(Decimal(self.amount) - self.hours_worked * self.hourly_rate) > Decimal('.01')
            ):
                # Check the math, while allowing for sub-penny rounding errors.
                # This could rely on the Decimal quantize() function instead, and getcontext().prec = 2.
                errors['amount'] = f'Must equal hours worked * rate (£{self.hours_worked * self.hourly_rate:.2f})'

        else:
            # Non hourly, so strip unneeded vars, set the weeks to 1
            self.hours_worked = None
            self.hourly_rate = None
            self.weeks = 1

        if errors:
            raise ValidationError(errors)

    def user_can_edit(self, user: User) -> bool:
        """Checks if a user has edit (and delete) permissions on the object"""
        if self.status_id == Statuses.RAISED:
            return (
                user.has_perm('tutor_payment.raise')
                and self.raised_by == user
                or user.has_perm('tutor_payment.approve')
            )
        if self.status_id == Statuses.APPROVED:
            return user.has_perm('tutor_payment.approve')
        if self.status_id == Statuses.TRANSFERRED:
            return user.has_perm('tutor_payment.transfer')
        return False


class PaymentRateQuerySet(models.QuerySet):
    def lookup(self, tag) -> Decimal:
        """Concise way of getting a payment_rate from a tag
        e.g. `marking_rate = PaymentRate.objects.lookup('marking')
        """
        return self.get(tag=tag).amount


class PaymentRate(models.Model):
    tag = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    type = models.CharField(max_length=64, null=True)  # A label used for grouping
    description = models.CharField(max_length=128)

    objects = PaymentRateQuerySet.as_manager()

    class Meta:
        db_table = 'tutor_fee_rate'

    def __str__(self) -> str:
        return f'£{self.amount:.2f} - {self.description}'


class PaymentStatus(models.Model):
    description = models.CharField(max_length=50)
    paid = models.BooleanField()

    class Meta:
        db_table = 'tutor_fee_status'

    def __str__(self) -> str:
        return str(self.description)


class PaymentType(models.Model):
    description = models.CharField(max_length=64)
    is_hourly = models.BooleanField()
    code = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'tutor_fee_type'

    def __str__(self) -> str:
        return str(self.description)

    def short_form(self) -> str:
        # Todo: reverse this.  Remove (hourly) from the descriptions, then update UI that needs it to add it
        return str(self).replace(' (hourly)', '')


@dataclass
class Schedule:
    months: int
    first_month: int
    label: str


schedules = [
    # (Payment count, starting month, label)
    # 3-Payments begin the month after the course starts, excepting michaelmas, where it's october (the same month)
    # 2-Payments begin a month later, concluding at the same time (half-length courses generally start later)
    Schedule(3, 10, 'Michaelmas - 3 payments (Oct-Dec)'),
    Schedule(2, 10, 'Michaelmas - 2 payments (Oct-Nov)'),
    Schedule(1, 1, 'Michaelmas - 1 payment (Jan)'),
    Schedule(3, 2, 'Hilary - 3 payments (Feb-Apr)'),
    Schedule(2, 2, 'Hilary - 2 payments (Feb-Mar)'),
    Schedule(1, 5, 'Hilary - 1 payment (May)'),
    Schedule(3, 5, 'Trinity - 3 payments (May-Jul)'),
    Schedule(2, 6, 'Trinity - 2 payments (Jun-Jul)'),
    Schedule(1, 8, 'Trinity - 1 payment (Aug)'),
    Schedule(2, 7, 'Summer - 2 payments (Jul-Aug)'),
    Schedule(1, 10, 'Summer - 1 payment (Oct)'),
    Schedule(6, 10, '2-Term Michaelmas & Hilary - 6 payments (Oct-Mar)'),
    Schedule(6, 2, '2-Term Hilary & Trinity - 6 payments (Feb-Jul)'),
]
