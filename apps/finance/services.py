from datetime import datetime
from decimal import Decimal
from typing import Optional

from django.db.models import Max

from apps.core.models import User

from . import models


def next_allocation() -> int:
    """Return the next allocation number available for use"""
    # todo: sort out using the max() method in redpot-legacy
    largest = models.Ledger.objects.aggregate(Max('allocation'))['allocation__max'] or 0
    return largest + 1


def insert_ledger(
    *,
    account_id: str,
    amount: Decimal,
    user: User,
    finance_code: str,
    narrative: str,
    type_id: int,
    timestamp: datetime = None,
    allocation: int = None,
    enrolment_id: Optional[int] = None,
    ref_no: str = None,
    account_only: bool = False,
    debtor_only: bool = False,
) -> None:
    """Creates a record and its corresponding debtors' control (Z300) record at the same time.
    +Amount increases debt owing (fees), -Amount decreases debt owing(payment)
    Posts both sides, unless account_only or debtor_only are used"""

    # Get a ledger allocation if required
    if not allocation:
        allocation = next_allocation()
    if not timestamp:
        timestamp = datetime.now()

    common = {
        'allocation': allocation,
        'enrolment_id': enrolment_id,
        'finance_code': finance_code,
        'narrative': narrative,
        'ref_no': ref_no,
        'timestamp': timestamp,
        'type_id': type_id,
        'created_by': user.username,
        'modified_by': user.username,
    }

    # Create the entries
    if not debtor_only:
        models.Ledger.objects.create(
            account_id=account_id,
            amount=-amount,  # Note the negative
            **common,
        )
    if not account_only:
        models.Ledger.objects.create(
            account_id=models.Accounts.DEBTOR,
            amount=amount,  # Note the positive
            **common,
        )
