from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from django.db.models import Max, Q

from apps.core.models import User
from apps.tutor.models import TutorModule
from apps.tutor_payment import models


def approve_payments(*, payment_ids: list[int], username: str) -> int:
    """Approve a set of payments, provided they pass the required checks
    and their approver matches the provided username"""
    payment_set = models.TutorPayment.objects.filter(
        status_id=models.Statuses.RAISED,
        approver=username,
        id__in=payment_ids,
    )
    approvable_payments = [payment.id for payment in payment_set if payment.approvable()]
    return models.TutorPayment.objects.filter(id__in=approvable_payments).update(
        status=models.Statuses.APPROVED, approved_by=username, approved_on=datetime.now()
    )


def create_teaching_fee(
    *,
    tutor_module: TutorModule,
    amount: Decimal,
    rate: Decimal,
    schedule: models.Schedule,
    raised_by: User,
    approver: User,
) -> None:
    """Generates a teaching fee spread across several payments according to a schedule (with separate holiday)"""
    holiday_amount = models.HOLIDAY_RATE * amount
    net_amount = amount - holiday_amount
    monthly_amount = net_amount / schedule.months
    # Get the beginning of the first payment month in the module's year
    assert tutor_module.module.start_date, 'Module lacks a start date'
    first_date = date(tutor_module.module.start_date.year, schedule.first_month, 1)
    # First day of following months
    dates = [first_date + relativedelta(months=n) for n in range(schedule.months)]
    raised_on = datetime.now()
    for idx, pay_date in enumerate(dates, 1):
        models.TutorPayment.objects.create(
            tutor_module=tutor_module,
            amount=monthly_amount,
            type_id=models.Types.TEACHING,
            pay_after=pay_date,
            details=f'Teaching fee (£{amount:.2f}) payment {idx}/{schedule.months}',
            approver=approver,
            hourly_rate=rate,
            hours_worked=monthly_amount / rate,
            weeks=4,
            raised_by=raised_by,
            raised_on=raised_on,
        )
    # Holiday pay - last month
    models.TutorPayment.objects.create(
        tutor_module=tutor_module,
        amount=holiday_amount,
        type_id=models.Types.HOLIDAY_PAY,
        pay_after=dates[-1],  # Last payment date
        details=f'Teaching fee (£{amount:.2f}) (holiday)',
        approver=approver,
        hourly_rate=rate,
        hours_worked=holiday_amount / rate,
        weeks=1,  # Not split across the month
        raised_by=raised_by,
        raised_on=raised_on,
    )


def next_batch() -> int:
    """Return the next batch number available for use"""
    largest = models.TutorPayment.objects.aggregate(Max('batch'))['batch__max'] or 0
    return largest + 1


def transfer_payments(*, pay_after: datetime, transferred_by: str) -> tuple[int, int]:
    """Batches all approved payments payable on the given date (pay_after before the date, or not set)"""
    batch = next_batch()

    count = models.TutorPayment.objects.filter(
        Q(pay_after__lte=pay_after) | Q(pay_after__isnull=True),
        status_id=models.Statuses.APPROVED,
    ).update(
        status_id=models.Statuses.TRANSFERRED,
        transferred_by=transferred_by,
        transferred_on=datetime.now(),
        batch=batch,
    )
    return batch, count
