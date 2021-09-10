from __future__ import annotations

from datetime import datetime
from itertools import cycle

from apps.core.utils import strings
from apps.core.utils.legacy.fpdf import ContedPDF
from apps.enrolment.models import Enrolment
from apps.student.models import Student

DATE_FORMAT = '%-d %b %Y'

# Todo: convert to weasyprint


class TranscriptPDF(ContedPDF):
    """Legacy fpdf template for student transcripts"""

    def __init__(self, level: str, print_header=False):
        self.print_header = print_header
        self.level = level
        super(TranscriptPDF, self).__init__()
        self.set_auto_page_break(True, margin=32)  # larger margin needed

    def header(self):
        if self.print_header:
            super(TranscriptPDF, self).header()
        else:
            # Transcripts, printed on our branded stationary, need no header
            self.cell(30, 42, '', 0, 1)

        if self.page_no() > 1:
            self.set_font('', 'B', 14)
            self.cell(0, 10, 'Record of CATS Points (Continued)', ln=1, align='C')

    def footer(self):
        # Footer is automatically included onto the bottom of every page
        # Position at 1.5 cm from bottom
        self.set_y(-32)
        self.cell(0, 4, '', 'T', 1)
        # Times italic 8
        self.set_font('', '', 8)
        self.set_text_color(60, 60, 60)

        self.multi_cell(0, 3, self.cats_text[self.level], 0, 1, 'L')

        self.ln(3)
        self.cell(0, 3, 'registry@conted.ox.ac.uk')

        # Page number
        self.cell(0, 3, 'Page %s/{nb}' % self.page_no(), align='R')

    cats_text = {
        'postgraduate': (
            'CATS points are credit points as defined under the nationally-recognised Credit Accumulation and '
            'Transfer Scheme. '
            'CATS points at FHEQ Level 7 are awarded for work of a standard equivalent to that expected of students '
            'on a Masters level programme. '
            'Two CATS points are equivalent to one ECTS credit.'
            '(180 CATS points at FHEQ Level 7 is equivalent to a Masters degree)'
        ),
        'undergraduate': (
            'CATS points are credit points as defined under the nationally recognised Credit Accumulation and '
            'Transfer Scheme. '
            'You may be able to transfer these credit points to other higher education institutions.  '
            'They are awarded at various levels within the Framework for Higher Education Qualifications (FHEQ): '
            'Level 4 equates to work of a standard equivalent to the first year of an undergraduate programme, '
            'Level 5 to the second year, and Level 6 to the third year.'
            'Two CATS points are equivalent to one ECTS credit.'
        ),
    }


def transcript(
    *,
    student: Student,
    address_lines: list[str],
    enrolments: list[Enrolment],
    level: str,
    header: bool,
) -> str:
    """Legacy routine: produces a transcript of all credit at a given level
    level takes 'undergraduate' and 'postgraduate' for undergraduate and postgraduate
    """

    pdf = TranscriptPDF(print_header=header, level=level)

    pdf.set_font('', 'B', 12)
    name = f"{student.title or ''} {student.firstname} {student.surname}".strip()
    pdf.cell(30, 4, name, ln=1)

    pdf.address_block(address_lines)

    pdf.ln(-8)
    pdf.set_font('', 'B', 10)
    pdf.cell(140, 4, 'Date ', align='R')
    pdf.set_font('', '', 10)
    pdf.cell(0, 4, datetime.now().strftime(DATE_FORMAT), ln=1)

    pdf.set_font('', 'B', 10)
    pdf.cell(140, 4, 'Registration ', align='R')
    pdf.set_font('', '', 10)
    pdf.cell(0, 4, str(student.husid).zfill(13), ln=1)

    pdf.ln(15)

    pdf.set_font('', 'B', 14)
    pdf.cell(0, 10, 'Record of CATS Points', ln=1, align='C')

    # And now a lovely table
    pdf.set_widths([24, 58, 20, 12, 22, 22, 12])

    def table_header():
        pdf.improved_multi_cell_table(
            header=['Module', 'Title', 'Result', 'FHEQ', 'Start date', 'End date', 'Points'],
            header_border=0,
            header_align='L',
        )

    table_header()

    pdf.set_aligns(['L', 'L', 'L', 'C', 'L', 'L', 'R'])

    # Stripy colors
    fill = cycle([True, False])
    pdf.set_fill_color(231, 231, 231)  # Bootstrap-like striped-table grey

    pdf.set_font('', '', 9)
    for enrolment in enrolments:
        # Handle multi_cells' inability to next-page in tables properly
        if pdf.y + 10 > pdf.page_break_trigger:
            pdf.add_page()
            table_header()
            pdf.set_font('', '', 9)

        pdf.improved_multi_cell_table(
            data=[
                enrolment.module.code,
                enrolment.module.title,
                str(enrolment.mark or '') if level == 'postgraduate' else 'Passed',
                str(enrolment.module.points_level.fheq_level),
                enrolment.module.start_date.strftime(DATE_FORMAT),
                enrolment.module.end_date.strftime(DATE_FORMAT),
                str(enrolment.points_awarded),
            ],
            draw_border=False,
            fill=next(fill),
        )

    pdf.set_widths([130, 25, 15])
    pdf.improved_multi_cell_table(
        header=['', 'Total', str(sum(enrolment.points_awarded for enrolment in enrolments))],
        header_border=0,
        header_align='R',
    )

    pdf.set_title(strings.normalize(f'{level.upper()} transcript: {student.firstname} {student.surname}'))

    return pdf.output(dest='S').encode('latin-1')
