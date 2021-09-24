from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from django.db import transaction
from django.db.models import Max

from apps.core.models import User
from apps.enrolment.models import Enrolment
from apps.fee.models import Accommodation, Catering, Fee
from apps.module.models import Module

from . import models


def next_allocation() -> int:
    """Return the next allocation number available for use"""
    # todo: sort out using the max() method in redpot-legacy
    largest = models.Ledger.objects.aggregate(Max('allocation'))['allocation__max'] or 0
    return largest + 1


@dataclass
class Transaction:
    """Holds both sides of a double-sided ledger transaction, to act as a useful return value.
    All functions calling _insert_account_line and _insert_debtor_line should return a Transaction
    """

    allocation: int
    account_line: models.Ledger
    debtor_lines: list[models.Ledger]


def _insert_account_line(
    *,
    account_code: str,
    amount: Decimal,
    user: User,
    finance_code: Optional[str],
    narrative: str,
    type_id: int,
    timestamp: datetime,
    allocation: int,
    enrolment_id: Optional[int] = None,
    ref_no: str = None,
) -> models.Ledger:
    """Produces the debtor side of a double-sided transaction"""
    return models.Ledger.objects.create(
        account_id=account_code,
        amount=-amount,  # Note the negative
        allocation=allocation,
        enrolment_id=enrolment_id,
        finance_code=finance_code,
        narrative=narrative,
        ref_no=ref_no,
        timestamp=timestamp,
        type_id=type_id,
        created_by=user.username,
        modified_by=user.username,
    )


def _insert_debtor_line(
    *,
    amount: Decimal,
    user: User,
    finance_code: Optional[str],
    narrative: str,
    type_id: int,
    timestamp: datetime,
    allocation: int,
    enrolment_id: Optional[int] = None,
    ref_no: str = None,
) -> models.Ledger:
    """Produces the account side of a double-sided transaction"""
    return models.Ledger.objects.create(
        account_id=models.Accounts.DEBTOR,
        amount=amount,  # Note the positive
        allocation=allocation,
        enrolment_id=enrolment_id,
        finance_code=finance_code,
        narrative=narrative,
        ref_no=ref_no,
        timestamp=timestamp,
        type_id=type_id,
        created_by=user.username,
        modified_by=user.username,
    )


@transaction.atomic
def insert_ledger(
    *,
    account_code: str,
    amount: Decimal,
    user: User,
    finance_code: Optional[str],
    narrative: str,
    type_id: int,
    timestamp: datetime = None,
    enrolment_id: Optional[int] = None,
    ref_no: str = None,
) -> Transaction:
    """Creates a double-sided transaction: posting to an account and debtors' control (Z300) at the same time.
    +ive amount increases debt owing (fees), -ive amount decreases debt owing(payment)
    """

    # Get a ledger allocation
    allocation = next_allocation()
    if not timestamp:
        timestamp = datetime.now()
    common: dict[str, Any] = {
        'allocation': allocation,
        'enrolment_id': enrolment_id,
        'finance_code': finance_code,
        'narrative': narrative,
        'ref_no': ref_no,
        'timestamp': timestamp,
        'type_id': type_id,
        'user': user,
    }

    # Create the entries
    account_line = _insert_account_line(
        account_code=account_code,
        amount=amount,
        **common,
    )
    debtor_line = _insert_debtor_line(
        amount=amount,
        **common,
    )
    return Transaction(allocation, account_line, [debtor_line])


@transaction.atomic
def add_enrolment_fee(*, enrolment_id: int, fee_id: int, discount: int = 0, user: User) -> Transaction:
    """Adds an existing module fee to an enrolment, including catering/accommodation records as required"""
    if discount >= 100:
        raise ValueError('Discount cannot be 100 or higher')

    fee = Fee.objects.select_related('type__account').get(pk=fee_id)
    ledger_transaction = insert_ledger(
        account_code=fee.type.account.code,
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
    return ledger_transaction


class DistributedPaymentTotalError(Exception):
    """Raised when the individual allocations don't sum to the total the amount"""


@transaction.atomic
def add_distributed_payment(
    *,
    narrative: str,
    amount: Decimal,
    type_id: int,
    user: User,
    enrolments: dict[int, Decimal],
    timestamp: Optional[datetime] = None,
) -> Transaction:
    """Distributes a payment among multiple enrolments, with a single payment row and multiple debt rows"""
    total = sum(enrolments.values())
    if amount != total:
        raise DistributedPaymentTotalError(f"Total does not match: {amount} vs {total}")

    allocation = next_allocation()
    if not timestamp:
        timestamp = datetime.now()  # identical timestamp for all rows

    debtor_lines = []
    for enrolment_id, sub_amount in enrolments.items():
        finance_code = Module.objects.get(enrolment__id=enrolment_id).finance_code
        line = _insert_debtor_line(
            finance_code=finance_code,
            narrative=narrative,
            amount=-sub_amount,
            type_id=type_id,
            allocation=allocation,
            enrolment_id=enrolment_id,
            user=user,
            timestamp=timestamp,
        )
        debtor_lines.append(line)

    # Corresponding total
    account_line = _insert_account_line(
        account_code=models.Accounts.CASH,
        finance_code='',
        narrative=narrative,
        amount=-amount,
        type_id=type_id,
        allocation=allocation,
        user=user,
        timestamp=timestamp,
    )
    return Transaction(allocation, account_line, debtor_lines)


@transaction.atomic
def transfer_funds(
    *,
    source_enrolment: Enrolment,
    target_enrolment: Enrolment,
    amount: Decimal,
    narrative: str,
    type_id: int,
    user: User,
) -> None:
    """Transfers funds from one enrolment to another"""
    common_args: dict[str, Any] = {
        'account_code': models.Accounts.CASH,
        'narrative': narrative,
        'user': user,
        'type_id': type_id,
        'timestamp': datetime.now(),
    }
    # Source enrolment lines
    insert_ledger(
        finance_code=source_enrolment.module.finance_code,
        amount=amount,
        enrolment_id=source_enrolment.id,
        **common_args,
    )
    # Target enrolment lines
    insert_ledger(
        finance_code=target_enrolment.module.finance_code,
        amount=-amount,
        enrolment_id=target_enrolment.id,
        **common_args,
    )


def next_batch() -> int:
    """Return the next batch available for use"""
    # todo: sort out using the max() method in redpot-legacy, or use the autonumber here (no!)
    largest = models.Ledger.objects.aggregate(Max('batch'))['batch__max'] or 0
    return largest + 1
