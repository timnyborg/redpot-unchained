import csv
import ftplib
import io
from datetime import date, datetime
from decimal import Decimal

from celery import shared_task

from redpot.settings import WPM_FTP as CONFIG

from .models import Invoice


@shared_task(name="repeating_card_payment_download")
def repeating_card_payment_download(filename: str = None) -> str:
    """
    Gets today's rcp payment data from WPM via ftp and creates invoice payments
    Can be overridden to download a particular file (e.g. a past date) via `filename`
    """

    # If unspecified, get today's payments file
    filename = filename or 'RCP_Payments_%s.csv' % date.today().strftime("%d%m%y")

    fieldnames = ['invoice_no', 'blank_1', 'blank_2', 'name', 'digits', 'card', 'amount', 'trans_id', 'date', 'status']
    file = _get_file_from_wpm_ftp(filename)
    payments = csv.DictReader(file, delimiter=',', fieldnames=fieldnames)

    payments_added = 0
    for payment in payments:
        if _is_valid_repeating_payment(payment):
            _add_repeating_payment(payment)
            payments_added += 1

    # Todo: Collect together basic payment info and send a summary to finance
    # Todo: Check the failures file and send info to finance

    return f'{filename}: {payments_added} payments'


def _get_file_from_wpm_ftp(filename: str) -> io.TextIOWrapper:
    """Log into the WPM ftp and download a given RCP result file"""
    ftp = ftplib.FTP_TLS(CONFIG['HOST'])
    # They use a self-signed cert, so no loading of the system's ssl context
    ftp.login(user=CONFIG['USER'], passwd=CONFIG['PASSWORD'])
    ftp.prot_p()  # Switch to a secure data connection
    ftp.cwd(CONFIG['DIRECTORY'])

    if filename not in ftp.nlst():
        raise FileNotFoundError('RCP file not found on WPM FTP server: %s' % filename)

    file = io.BytesIO()
    ftp.retrbinary(f"RETR {filename}", file.write)
    file.seek(0)
    return io.TextIOWrapper(file)


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
    invoice = Invoice.objects.filter(number=payment['invoice_no']).first()  # noqa: F841 # todo: remove when complete

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
