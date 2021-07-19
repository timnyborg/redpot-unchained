from datetime import datetime
from decimal import Decimal
from typing import Optional

from django.db.models import Max

from apps.core.models import User
from apps.fee.models import Accommodation, Catering, Fee

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
    finance_code: Optional[str],
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


def add_enrolment_fee(*, enrolment_id: int, fee_id: int, discount: int = 0, user: User) -> None:
    """Adds an existing module fee to an enrolment, including catering/accommodation records as required"""
    if discount >= 100:
        raise ValueError('Discount cannot be 100 or higher')

    fee = Fee.objects.select_related('type__account').get(pk=fee_id)
    insert_ledger(
        account_id=fee.type.account.code,
        finance_code=fee.finance_code,
        narrative=fee.description,
        amount=fee.amount * (1 - Decimal(discount) / 100),
        type_id=models.TransactionTypes.FEE,
        enrolment_id=enrolment_id,
        ref_no=str(fee.id),
        user=user,
    )

    # If the fee is victual-related, add in a catering line.
    if fee.is_catering:
        Catering.objects.create(fee=fee, enrolment_id=enrolment_id)

    # If the fee is accomodation-related, add in an accommodation line.
    if fee.is_single_accom or fee.is_twin_accom:
        Accommodation.objects.create(
            type=Accommodation.Types.SINGLE if fee.is_single_accom else Accommodation.Types.TWIN,
            limit=fee.limit,
            enrolment_id=enrolment_id,
        )
