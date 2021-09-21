from __future__ import annotations

from datetime import datetime

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
