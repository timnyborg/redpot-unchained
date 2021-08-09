from __future__ import annotations

import csv
import io
from datetime import datetime
from decimal import Decimal
from typing import IO, Iterable, Optional

from django.contrib import auth
from django.db import transaction
from django.db.models import Max

from apps.core.models import User
from apps.enrolment.models import Enrolment
from apps.finance import services as finance_services
from apps.finance.models import Ledger, TransactionTypes

from . import models


def next_invoice_number() -> int:
    """Return the next invoice number available for use"""
    # todo: sort out using the max() method in redpot-legacy, or use the autonumber here (no!)
    largest = models.Invoice.objects.aggregate(Max('number'))['number__max'] or 0
    return largest + 1


@transaction.atomic()
def create_invoice(*, amount: Decimal, fees: Iterable[Ledger], user: User, **kwargs) -> models.Invoice:
    """Creates an invoice and attaches fees"""
    invoice = models.Invoice.objects.create(
        amount=amount,
        number=next_invoice_number(),
        created_by=user.username,
        modified_by=user.username,
        **kwargs,
    )
    for index, ledger in enumerate(fees, start=1):
        invoice.ledger_items.add(
            ledger,
            through_defaults={
                'item_no': index,
                'allocation': invoice,
            },
        )
    return invoice


def add_repeating_payments_from_file(*, file: IO[bytes]) -> int:
    """Create financial records for all RCP payments in a file object, returning the number that succeeded"""

    FIELDNAMES = ['invoice_no', 'blank_1', 'blank_2', 'name', 'digits', 'card', 'amount', 'trans_id', 'date', 'status']
    # convert BytesIO objects (which file uploads and ftp provide) to return strings, which csv requires
    file = io.TextIOWrapper(file)
    payments = csv.DictReader(file, delimiter=',', fieldnames=FIELDNAMES)

    valid_payments = list(filter(_is_valid_repeating_payment, payments))
    for payment in valid_payments:
        _add_repeating_payment(payment)

    return len(valid_payments)


def _is_valid_repeating_payment(row: dict) -> bool:
    """Check that an rcp item is a payment that can be applied to an invoice"""
    return (
        row['status'] == 'success'
        and row['invoice_no'].isdigit()  # exclude non-invoice items (FOLL)
        and Decimal(row['amount']) > 0  # exclude rcp refunds, which will have already been listed in the ledger
    )


def _add_repeating_payment(payment: dict) -> None:
    """Take an RCP dict, and create an invoice payment from it"""
    payment_date = datetime.strptime(payment['date'], '%d/%m/%y %H:%M')  # noqa: F841 # todo: remove when complete
    narrative = (
        f"{payment['name']}, card: {payment['card']}, digits: {payment['digits']}, trans: {payment['trans_id']}"[:128]
    )
    invoice = models.Invoice.objects.get(number=payment['invoice_no'])
    service_user = auth.get_user_model().objects.get(username='service_user')

    add_payment(
        invoice=invoice,
        amount=payment['amount'],
        type_id=TransactionTypes.RCP,
        narrative=narrative,
        timestamp=payment_date,
        user=service_user,
    )


@transaction.atomic
def add_credit(
    *,
    invoice: models.Invoice,
    enrolment: Enrolment,
    account_code: str,
    type_id: int,
    amount: Decimal,
    narrative: str,
    user: User,
) -> None:
    """Add a credit to an invoice (on a specific enrolment)"""
    ledger_transaction = finance_services.insert_ledger(
        account_code=account_code,
        finance_code=enrolment.module.finance_code,
        narrative=narrative,
        amount=-amount,
        type_id=type_id,
        enrolment_id=enrolment.id,
        user=user,
    )
    attach_transaction_to_invoice(transaction=ledger_transaction, invoice=invoice)


class NoValidEnrolmentsError(Exception):
    """Raised when trying to create a financial transaction without a valid enrolment"""


def _split_by_owing(*, owing: Decimal, total_owing: Decimal, payment_amount: Decimal):
    """Allocate payment by enrolment, in proportion to their amount, rounding to the penny"""
    return Decimal(owing / total_owing * payment_amount).quantize(Decimal('.01'))


def _split_evenly(*, payment_amount: Decimal, split_by: int):
    """Distribute evently.  For rare cases where we're allocating to a settled invoice (e.g. finance amendments)
    Rounds to the penny
    """
    return Decimal(payment_amount / split_by).quantize(Decimal('.01'))  # Round to the nearest penny


# todo: test that this will allocate correctly if an invoiced enrolment contains non-invoiced fees/balance
@transaction.atomic
def add_payment(
    invoice: models.Invoice,
    amount: Decimal,
    type_id: int,
    user: User,
    narrative: str,
    enrolment: Optional[Enrolment] = None,
    timestamp: Optional[datetime] = None,
):
    """
    Automatically distribute a payment to enrolments on an invoice according to balance
    Specifying `enrolment` allows the payment to be applied to only one part of an invoice (typically when
    finance moves money about)
    """

    queryset = Enrolment.objects.filter(ledger__invoice=invoice).with_balance()
    if enrolment:
        queryset = queryset.filter(id=enrolment.id)
    enrolments = list(queryset)
    if not enrolments:
        raise NoValidEnrolmentsError('Invoice has no enrolments')

    total_owing = invoice.balance()

    allocations: dict[int, Decimal] = {}
    for enrolment in enrolments:
        if total_owing:
            allocated = _split_by_owing(owing=enrolment.balance, total_owing=total_owing, payment_amount=amount)
        else:
            allocated = _split_evenly(payment_amount=amount, split_by=len(enrolments))
        allocations[enrolment.id] = allocated

    # Check for a difference due to rounding
    diff = sum(allocations.values()) - amount
    # And allocate the difference to the first enrolment
    allocations[enrolments[0].id] -= diff

    ledger_transaction = finance_services.add_distributed_payment(
        narrative=narrative,
        amount=amount,
        type_id=type_id,
        user=user,
        enrolments=allocations,
        timestamp=timestamp,
    )
    attach_transaction_to_invoice(transaction=ledger_transaction, invoice=invoice)


def attach_transaction_to_invoice(
    *,
    transaction: finance_services.Transaction,
    invoice: models.Invoice,
):
    """Attach a credit or payment transaction to an invoice"""
    invoice.ledger_items.add(
        *transaction.debtor_lines,
        through_defaults={
            'allocation': invoice,
            'item_no': 0,  # payment/credit, not an invoiced line
        },
    )
