from __future__ import annotations

from datetime import date
from itertools import cycle

from django.db.models import Prefetch

from apps.core.utils import strings
from apps.core.utils.legacy.fpdf import ContedPDF
from apps.core.utils.postal import FormattedAddress
from apps.enrolment.models import Enrolment
from apps.finance.models import Ledger
from apps.student import models

DATE_FORMAT = '%-d %b %Y'

# todo: convert to weasyprint


def create_statement(student: models.Student) -> bytes:
    address = student.get_default_address()
    enrolments = list(
        Enrolment.objects.filter(qa__student=student)
        .order_by('-module__start_date', 'module__code')
        .select_related('module', 'status')
        .prefetch_related(
            # Filter ledger_set to debt-only items here, rather than during rendering.
            Prefetch(
                'ledger_set',
                queryset=Ledger.objects.debts()
                .select_related('type', 'invoice_ledger__invoice')
                .order_by('-timestamp'),
            )
        )
    )
    return _render_statement(
        student=student,
        address=address,
        enrolments=enrolments,
    )


def _render_statement(*, student: models.Student, address: models.Address, enrolments: list[Enrolment]) -> bytes:
    pdf = ContedPDF()

    pdf.bottom_left_text = 'In the event of a query please contact: finance@conted.ox.ac.uk'

    pdf.set_font_size(12)
    name = student.formal_name
    pdf.cell(30, 4, name)
    pdf.cell(0, 4, date.today().strftime(DATE_FORMAT), 0, 1, 'R')

    for line in FormattedAddress(address):
        pdf.cell(30, 5, line, ln=1)

    pdf.ln(24)
    pdf.set_font('', 'B', 14)
    pdf.multi_cell(0, 4, f'Financial statement for {student.firstname} {student.surname}', align='L')
    pdf.ln(8)

    pdf.set_fill_color(231, 231, 231)  # Bootstrap-like striped-table grey

    # Create the table header, data array and column widths to pass to the table function
    pdf.set_widths([25, 89, 16, 18, 22])
    pdf.set_aligns(['L', 'L', 'L', 'L', 'R'])

    for enrolment in enrolments:
        fill = cycle([True, False])
        pdf.set_font('', 'B', 11)
        pdf.multi_cell(170, 4, f'{enrolment.module.title} ({enrolment.module.code}) ({enrolment.status})')

        pdf.set_font('', '', 9)
        for fee in enrolment.ledger_set.all():
            data = [
                fee.timestamp.strftime(DATE_FORMAT),
                fee.narrative or '',
                str(fee.invoice_ledger.invoice) if hasattr(fee, 'invoice_ledger') else '',
                fee.type.description,
                f'£{fee.amount:.2f}',
            ]

            pdf.improved_multi_cell_table(data=data, draw_border=False, fill=next(fill))

        # Balance footer for each table
        pdf.set_font('', 'B', 9)
        enrolment.total = sum(fee.amount for fee in enrolment.ledger_set.all())
        pdf.improved_multi_cell_table(
            data=['', '', '', 'Balance', f'£{enrolment.total:.2f}'],
            draw_border=False,
        )

        pdf.ln(4)

    pdf.ln(4)
    pdf.set_font('', 'B', 12)
    pdf.cell(114)
    pdf.cell(34, 4, 'Total balance')
    total = sum(enrolment.total for enrolment in enrolments)
    pdf.cell(22, 4, f'£{total:.2f}', align='R', ln=1)

    pdf.set_title(strings.normalize(f'Financial statement for {student.firstname} {student.surname}'))
    return pdf.output(dest='S').encode('latin-1')
