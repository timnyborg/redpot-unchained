from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from django.db import transaction
from django.db.models import Max

from apps.core.models import User

from . import models


def next_invoice_number() -> int:
    """Return the next invoice number available for use"""
    # todo: sort out using the max() method in redpot-legacy, or use the autonumber here (no!)
    largest = models.Invoice.objects.aggregate(Max('number'))['number__max'] or 0
    return largest + 1


@transaction.atomic()
def create_invoice(*, amount: Decimal, fees: Iterable[models.Ledger], user: User, **kwargs) -> models.Invoice:
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
