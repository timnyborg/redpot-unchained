from __future__ import annotations

import textwrap
from datetime import datetime
from typing import Optional

from apps.core.utils.legacy.fpdf import ContedPDF
from apps.core.utils.postal import FormattedAddress
from apps.invoice.models import Invoice
from apps.student.models import Student

from . import models

DATE_FORMAT = '%-d %b %Y'


def create_receipt(*, allocation: int, student: Optional[Student] = None) -> bytes:
    """Creates the context for rendering a receipt, then calls the rendering method.  Separation of argument logic from
    rendering will make for an easy move to weasyprint"""
    cash_line = models.Ledger.objects.cash_control().get(allocation=allocation)
    debt_lines = list(
        models.Ledger.objects.filter(allocation=allocation)
        .debts()
        .select_related('enrolment', 'enrolment__module', 'enrolment__qa__student')
    )

    # Use the first ledger item for accessing invoice, student, etc.
    first_item = debt_lines[0]
    if not student:
        student = first_item.enrolment.qa.student
    invoice: Optional[Invoice] = first_item.invoice_ledger.invoice if hasattr(first_item, 'invoice_ledger') else None

    # The address block displays invoice details if they exist
    if invoice:
        addressed_to = invoice.invoiced_to
        address_block = FormattedAddress(invoice).as_list()
    else:
        addressed_to = f"{student.title or ''} {student.firstname} {student.surname}".strip()
        address_block = FormattedAddress(student.get_billing_address()).as_list()

    return _render_receipt(
        cash_line=cash_line,
        debt_lines=debt_lines,
        address_block=address_block,
        addressed_to=addressed_to,
        invoice=invoice,
    )


def _render_receipt(
    *,
    cash_line: models.Ledger,
    debt_lines: list[models.Ledger],
    address_block: list[str],
    addressed_to: str,
    invoice: Optional[Invoice],
) -> bytes:
    """Render a PDF receipt"""
    pdf = ContedPDF()
    pdf.bottom_left_text = 'In the event of a query please contact: finance@conted.ox.ac.uk'
    pdf.bottom_right_text = 'VAT number: GB 125 5067 30'

    pdf.set_font('', '', 12)

    pdf.cell(30, 4, addressed_to)
    pdf.cell(0, 4, datetime.now().strftime(DATE_FORMAT), 0, 1, 'R')

    pdf.address_block(address_block)
    pdf.ln(16)

    pdf.set_font('', 'B', 14)
    pdf.cell(0, 10, 'RECEIPT OF PAYMENT', ln=1)

    pdf.ln(2)
    pdf.set_font('', '', 12)
    if invoice:
        pdf.cell(0, 5, f'Invoice: {invoice.prefix}{invoice.number}', ln=1)

    pdf.cell(0, 5, f'Receipt date: {cash_line.created_on.strftime(DATE_FORMAT)}', ln=1)
    pdf.ln(4)

    pdf.set_fill_color(231, 231, 231)  # Bootstrap-like striped-table grey

    # Total paid table
    pdf.improved_table(
        ('Student', 'Course', 'Amount paid'),
        [
            (
                f'{line.enrolment.qa.student.firstname} {line.enrolment.qa.student.surname}',
                textwrap.shorten(line.enrolment.module.title, 50, placeholder='…'),
                f'£{-line.amount:.2f}',
            )
            for line in debt_lines
        ],
        (65, 82, 23),
        ('Total paid', f'£{cash_line.amount:.2f}'),
        (145, 25),
        fill=[True, False],
    )

    # Output everything onto PDF
    pdf.set_title(f'Receipt {cash_line.allocation}')
    return pdf.output(dest='S').encode('latin-1')
