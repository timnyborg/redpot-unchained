from __future__ import annotations

from datetime import date
from itertools import cycle

from apps.core.utils.legacy.fpdf import ContedPDF
from apps.core.utils.postal import FormattedAddress
from apps.core.utils.strings import normalize
from apps.finance.models import Ledger
from apps.student.models import Address, Student

from . import models

DATE_FORMAT = '%-d %b %Y'

# Todo: convert to weasyprint


def create_statement(enrolment: models.Enrolment) -> bytes:
    student = enrolment.qa.student
    address = student.get_default_address()
    # todo: is the student select_related needed? Surely it's always student
    fees = list(enrolment.ledger_set.debts().select_related('type').order_by('timestamp', 'id'))
    return _render_statement(
        enrolment=enrolment,
        student=student,
        address=address,
        fees=fees,
    )


def _render_statement(enrolment: models.Enrolment, student: Student, address: Address, fees: list[Ledger]) -> bytes:
    module = enrolment.module
    pdf = ContedPDF()
    pdf.bottom_left_text = (
        f"In the event of a query please contact: {module.phone or ''} "  # todo: remove '' once phone null=False
        f"({module.email or 'finance@conted.ox.ac.uk'})"
    )

    # Creating name and address information on the left
    pdf.set_font_size(12)
    name = f"{student.title or ''} {student.firstname} {student.surname}".strip()
    pdf.cell(30, 4, name)
    pdf.cell(0, 4, date.today().strftime(DATE_FORMAT), 0, 1, 'R')

    pdf.address_block(FormattedAddress(address))

    # Invoice specific text above tables
    pdf.ln(40)
    pdf.multi_cell(0, 4, f'Statement for course: {module.title} ({module.code})', align='L')
    if module.start_date:
        pdf.set_font_size(9)
        pdf.cell(0, 10, f'Starts {module.start_date.strftime(DATE_FORMAT)}', ln=1)
        pdf.set_font_size(10)

    # Stripy colors
    fill = cycle([True, False])
    pdf.set_fill_color(231, 231, 231)  # Bootstrap-like striped-table grey

    # Create the table header, data array and column widths to pass to the table function
    pdf.set_widths([100, 40, 30])
    pdf.set_aligns(['L', 'L', 'R'])

    for fee in fees:
        data = [fee.narrative, fee.type.description, f'£{fee.amount:.2f}']
        pdf.improved_multi_cell_table(data=data, draw_border=False, fill=next(fill))

    footer = ['Remaining', f'£{enrolment.get_balance():.2f}']
    pdf.set_widths([150, 20])
    pdf.improved_multi_cell_table(footer=footer, footer_border=False)

    pdf.set_title(normalize(f'Statement: {module.code} - {student.surname}'))
    return pdf.output(dest='S').encode('latin-1')
