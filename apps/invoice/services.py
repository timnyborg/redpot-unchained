from __future__ import annotations

import csv
import io
from datetime import datetime
from decimal import Decimal
from typing import IO, Iterable

from django.db import transaction
from django.db.models import Max

from apps.core.models import User
from apps.finance.models import Ledger

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
    invoice = models.Invoice.objects.filter(  # noqa: F841 # todo: remove when complete
        number=payment['invoice_no']
    ).first()

    # todo: implement invoice payment
    # insert_invoice_payment(
    #     invoice.id,
    #     amount,
    #     17,  # RCP
    #     narrative,
    #     date=payment_date
    # )

    # debugging while above not implemented
    print(narrative)
