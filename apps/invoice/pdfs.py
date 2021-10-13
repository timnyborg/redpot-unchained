from __future__ import annotations

from datetime import date
from itertools import cycle

from apps.core.utils.legacy.fpdf import ContedPDF
from apps.core.utils.postal import FormattedAddress
from apps.finance.models import Ledger
from apps.invoice import models

DATE_FORMAT = '%d %b %Y'

# Todo: convert to weasyprint


def create_invoice(invoice: models.Invoice) -> bytes:
    # separated out model access from rendering to ease migration to weasyprint
    fees = (
        invoice.get_fees()
        .select_related('enrolment__module', 'enrolment__qa__student')
        .order_by('enrolment__qa__student__surname', 'enrolment__qa__student__firstname', 'enrolment__id')
    )
    return _generate_invoice(invoice=invoice, fees=fees)


def _generate_invoice(*, invoice: models.Invoice, fees: list[Ledger]) -> bytes:
    pdf = ContedPDF()
    pdf.bottom_left_text = (
        "In the event of a query please contact: "
        f"{invoice.contact_person} {invoice.contact_phone} ({invoice.contact_email or 'finance@conted.ox.ac.uk'})"
    )
    pdf.bottom_right_text = 'VAT number: GB 125 5067 30'

    # Creating name and address information on the left, invoice details on the right
    block = [invoice.invoiced_to]
    if invoice.fao:
        block.append(invoice.fao)
    block.extend(FormattedAddress(invoice).as_list())

    pdf.address_block(block)

    # Move up 3 lines
    pdf.ln(-12)

    pdf.set_font('', 'B', 10)
    pdf.cell(148, 4, 'Invoice number: ', align='R')
    pdf.set_font('', '', 10)
    pdf.cell(0, 4, f'{invoice.prefix}{invoice.number}', ln=1)
    pdf.set_font('', 'B', 10)
    pdf.cell(148, 4, 'Invoice date: ', align='R')
    pdf.set_font('', '', 10)
    pdf.cell(0, 4, invoice.date.strftime(DATE_FORMAT), ln=1)
    pdf.set_font('', 'B', 10)
    pdf.cell(148, 4, 'Payment due date: ', align='R')
    pdf.set_font('', '', 10)
    pdf.cell(0, 4, invoice.due_date.strftime(DATE_FORMAT) if invoice.due_date else '', ln=1)

    if invoice.ref_no:
        pdf.set_font('', 'B', 12)
        pdf.ln(4)
        pdf.cell(48, 4, 'Customer Reference #: ')
        pdf.set_font('', '', 12)
        pdf.cell(30, 4, invoice.ref_no, ln=1)

    if invoice.vat_no:
        pdf.set_font('', 'B', 12)
        pdf.ln(4)
        pdf.cell(48, 4, 'VAT #: ')
        pdf.set_font('', '', 12)
        pdf.cell(30, 4, invoice.vat_no, ln=1)

    # End name and address panel
    pdf.ln(16)

    pdf.set_font('', 'B', 14)
    pdf.cell(0, 10, 'INVOICE', 0, 1, 'C')

    pdf.ln(4)

    fill = cycle([False, True])
    pdf.set_fill_color(231, 231, 231)  # Bootstrap-like striped-table grey
    pdf.set_aligns(['L', 'L', 'R'])
    pdf.set_font('arial_ttf', 'B', 10)

    # Create the table header, data array and column widths to pass to the table function
    if invoice.custom_narrative:
        # Squeeze out the student column for custom narratives
        pdf.set_widths([140, 30])
        header = ['Description', 'Amount']
    else:
        pdf.set_widths([40, 100, 30])
        header = ['Student', 'Description', 'Amount']

    pdf.improved_multi_cell_table(data=header, draw_border=False, fill=next(fill))

    # Fee loop
    pdf.set_font('arial_ttf', '', 10)
    if invoice.custom_narrative:
        data = [invoice.narrative, '']
        pdf.improved_multi_cell_table(data=data, draw_border=False, fill=next(fill))
        pdf.set_widths([40, 100, 30])  # Resume three columns, like a normal invoice
    else:
        current_student = ''
        for fee in fees:
            # old todo: Use itertools.groupby()! Make this properly grouped and looped.  One loop for each enrolment,
            #  heading with the student and title, then rows for each fee.
            student = fee.enrolment.qa.student
            studentname = f'{student.firstname} {student.surname}'
            if studentname != current_student:
                data = [studentname, 'Breakdown of fees payable', '']
                pdf.improved_multi_cell_table(data=data, draw_border=False, fill=next(fill))
                current_student = studentname

            data = [
                '',
                f'{fee.enrolment.module.title} - {fee.narrative}',
                f'£{fee.amount:,.2f}',
            ]
            pdf.improved_multi_cell_table(data=data, draw_border=False, fill=next(fill))

    pdf.improved_multi_cell_table(data=['', '', ''], draw_border=False, fill=False)
    pdf.improved_multi_cell_table(data=['', 'VAT', '£0.00'], draw_border=False, fill=True)

    footer = ['Invoice total', f'£{invoice.amount:,.2f}']
    pdf.set_widths([140, 30])
    pdf.set_aligns(['R', 'R'])

    pdf.set_font('arial_ttf', 'B', 10)
    pdf.improved_multi_cell_table(data=footer, draw_border=False, fill=False)

    pdf.ln(20)

    # Payment methods and T&Cs on a separate page
    pdf.add_page()
    pdf.ln(5)
    pdf.set_font('', 'B', 12)
    pdf.cell(0, 5, 'Payment methods', ln=1)
    pdf.set_font_size(8)
    pdf.cell(5)
    pdf.cell(0, 5, '1) Secure online payments (including payment plans)', ln=1)
    pdf.set_font('', '', 8)
    pdf.cell(10)
    pdf.multi_cell(
        0,
        4,
        'Payment can be made using a debit or credit card at the following address:\n'
        'https://www.conted.ox.ac.uk/invoicepayments',
        0,
        'L',
    )
    pdf.ln(1)
    pdf.cell(10)
    pdf.cell(0, 4, 'You should provide the following information:', ln=1)
    pdf.set_font('', 'B', 8)
    pdf.cell(20)
    pdf.cell(0, 4, f'Invoice number: {invoice.prefix}{invoice.number}', ln=1)
    pdf.cell(20)
    pdf.cell(0, 4, f'Name on invoice: {invoice.invoiced_to}', ln=1)
    pdf.set_font('', '', 8)
    pdf.ln(1)
    pdf.cell(10)
    pdf.cell(
        0,
        5,
        'If you have been offered the choice to pay an invoice by instalments, the payment options will be displayed.',
        ln=1,
    )

    pdf.ln(2)
    pdf.cell(10)

    txt = (
        'All online transactions will appear on your statement as Oxford University internet GBR. '
        'Customer card details are managed securely, '
        'and are not stored by the Department for Continuing Education.'
    )
    pdf.basic_table('', [[txt]], [160], ['LTRB'], font_type='small', cell_type='multi_cell')

    pdf.ln(1)
    pdf.cell(10)
    pdf.cell(0, 5, 'Notes for card payments', ln=1)
    pdf.cell(15)
    pdf.multi_cell(
        0,
        4,
        '• For non-UK cardholders, it is recommended that you contact your card provider to let them know in advance '
        'that you will be making a payment to the University of Oxford.',
        0,
        'L',
    )
    pdf.cell(15)
    pdf.cell(0, 4, '• If you experience problems, please email finance@conted.ox.ac.uk', ln=1)
    pdf.cell(15)
    pdf.cell(0, 4, '• Allow 3 working days for payment by card.', ln=1)

    pdf.set_font('', 'B', 8)
    pdf.ln(2)
    pdf.cell(5)
    pdf.cell(0, 5, '2) Direct bank transfer', ln=1)
    pdf.set_font('', '', 8)

    txt = [
        ['', 'Bank:', 'Barclays Bank'],
        ['', 'Address:', 'Oxford City Office, PO Box 333, 54 Cornmarket Street, Oxford, UK, OX1 3HS'],
        ['', 'Sort code:', '20-65-46'],
        ['', 'Account name:', 'University of Oxford'],
        ['', 'Account number:', '30103489'],
        ['', 'IBAN:', 'GB23BARC20654630103489'],
        ['', 'SWIFT:', 'BARCGB22'],
    ]
    col_widths = [15, 30, 138]
    borders = [''] * len(txt) * 3
    pdf.basic_table('', txt, col_widths, borders, font_type='small', cell_type='Cell')

    pdf.ln(1)
    pdf.cell(10)

    pdf.cell(0, 5, 'Notes for bank transfers:', ln=1)
    pdf.cell(15)
    pdf.cell(0, 4, '• Quote the invoice number as a reference for the payment.', ln=1)
    pdf.cell(15)
    pdf.cell(0, 4, '• Allow 5 working days for payment by bank transfer.', ln=1)

    pdf.ln(1)
    pdf.cell(5)
    pdf.set_font('', 'B', 8)
    pdf.cell(0, 5, '3) Other payment methods', ln=1)
    pdf.set_font('', '', 8)
    pdf.cell(10)

    pdf.cell(0, 4, '3.1 Setting up a payment plan by telephone; contact Finance at +44 (0)1865 280313.', ln=1)
    pdf.cell(10)
    pdf.cell(0, 4, '3.2 Cheque payments by post (please note that post-dated cheques will not be accepted).', ln=1)
    pdf.cell(10)
    pdf.cell(
        0,
        4,
        '3.3 If you are unable to pay using any of the above methods, please contact Finance at +44 (0)1865 270394.',
        ln=1,
    )
    pdf.ln(1)
    pdf.cell(10)

    pdf.cell(0, 5, 'Notes for other payment methods:', ln=1)
    pdf.cell(15)
    pdf.cell(
        0, 4, '• Cheques must be drawn on a UK bank account and made payable to "University of Oxford - OUDCE".', ln=1
    )
    pdf.cell(15)
    pdf.cell(
        0,
        4,
        '• Quote the invoice number as a reference for the payment (if paying by cheque, '
        'please write the invoice number on the back).',
        ln=1,
    )
    pdf.cell(15)
    pdf.cell(0, 4, '• Allow 5 working days for cheques to be processed and to clear.', ln=1)

    pdf.ln(5)
    pdf.set_font('', 'B', 12)
    pdf.cell(0, 5, 'Terms and Conditions', ln=1)
    pdf.set_font('', '', 8)
    pdf.cell(5)
    pdf.multi_cell(
        0,
        4,
        'Under the regulation of the EU we do not charge VAT on services provided to VAT-registered businesses in '
        'other member countries. According to the reverse-charge regulation tax liability transfers to the recipient '
        'of services.',
    )
    pdf.cell(5)
    pdf.multi_cell(
        0,
        4,
        'Payments must be made by the due date specified, irrespective of which payment method is used. '
        'Full terms and conditions are available at: https://www.conted.ox.ac.uk/terms-and-conditions',
    )

    pdf.set_title(f'Invoice {invoice.prefix}{invoice.number}')
    return pdf.output(dest='S').encode('latin-1')


def create_statement(invoice: models.Invoice) -> bytes:
    payments = list(invoice.get_payments().select_related('type').order_by('timestamp'))
    try:
        scheduled_payments = list(invoice.payment_plan.scheduled_payments.order_by('due_date'))
    except models.PaymentPlan.DoesNotExist:
        scheduled_payments = []
    return _generate_statement(invoice=invoice, payments=payments, scheduled_payments=scheduled_payments)


def _generate_statement(
    *, invoice: models.Invoice, payments: list[Ledger], scheduled_payments: list[models.ScheduledPayment]
) -> bytes:
    # todo: when converting to weasyprint, much of the top matter and footer is shared with invoice,
    #  so use a common template
    pdf = ContedPDF()
    pdf.bottom_left_text = (
        "In the event of a query please contact: "
        f"{invoice.contact_person} {invoice.contact_phone} ({invoice.contact_email or 'finance@conted.ox.ac.uk'})"
    )
    pdf.bottom_right_text = 'VAT number: GB 125 5067 30'

    # Creating name and address information on the left, invoice details on the right
    block = [invoice.invoiced_to]
    if invoice.fao:
        block.append(invoice.fao)
    block.extend(FormattedAddress(invoice).as_list())
    pdf.address_block(block)

    pdf.ln(-4)
    pdf.cell(0, 4, date.today().strftime(DATE_FORMAT), 0, 1, 'R')
    pdf.ln(20)

    pdf.set_font('', 'B', 14)
    pdf.cell(0, 10, 'STATEMENT', 0, 1, 'C')

    pdf.ln(10)
    pdf.set_font('', 'B', 12)
    pdf.cell(60, 4, f'Invoice {invoice.prefix}{invoice.number}', align='L')
    pdf.cell(80, 4, 'Amount', align='R')
    pdf.cell(30, 4, f'£{invoice.amount:.2f}', align='R')

    pdf.ln(10)
    pdf.set_font('', 'B', 12)
    pdf.multi_cell(0, 4, 'Payments', align='L')
    pdf.ln(2)

    payment_total = sum(-payment.amount for payment in payments)
    pdf.PrettyTable(
        body=[
            [
                payment.timestamp.strftime(DATE_FORMAT),
                payment.narrative,
                payment.type.description,
                f'£{-payment.amount:.2f}',
            ]
            for payment in payments
        ]
        if payments
        else [['None', '', '', '']],
        footer=['Total', f'£{payment_total:.2f}'],
        width={'body': [25, 97, 24, 24], 'footer': [132, 38]},
        fill={'body': [(231, 231, 231), False]},
        align={'body': ['L', 'L', 'L', 'R'], 'footer': 'R'},
    ).render()

    pdf.ln(8)
    pdf.set_font('', 'B', 12)
    pdf.cell(140, 0, 'Balance', align='R')
    pdf.cell(30, 0, f'£{invoice.balance:.2f}', align='R')

    if scheduled_payments:
        pdf.ln(8)
        pdf.set_font('', 'B', 12)
        pdf.multi_cell(0, 4, 'Scheduled payments', align='L')
        pdf.ln(2)
        pdf.PrettyTable(
            body=[[row.due_date.strftime(DATE_FORMAT), f'£{row.amount:.2f}'] for row in scheduled_payments],
            width={'body': [30, 50]},
            fill={'body': [(231, 231, 231), False]},
            align={'body': ['L', 'R']},
        ).render()

    pdf.set_title(f'Invoice statement {invoice.prefix}{invoice.number}')
    return pdf.output(dest='S').encode('latin-1')
