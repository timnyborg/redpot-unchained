import csv
from decimal import Decimal
from datetime import datetime, date
from ftplib import FTP_TLS
from io import StringIO

from celery import shared_task

from redpot.settings import WPM_FTP as CONFIG

from .models import Invoice


@shared_task(name="wpm_ftp_download")
def wpm_ftp_download(filename=None):
    """
        Gets today's rcp payment data from WPM via ftp and creates invoice payments
        Can be overridden to download a particular file (e.g. a past date) via `filename`
    """
    # Log into wpm ftp
    ftp = FTP_TLS(CONFIG['HOST'])
    # They use a self-signed cert, so no loading of the system's ssl context
    ftp.login(user=CONFIG['USER'], passwd=CONFIG['PASSWORD'])
    ftp.prot_p()  # Switch to a secure data connection
    ftp.cwd(CONFIG['DIRECTORY'])

    # Getting today's csv file
    filename = filename or 'RCP_Payments_%s.csv' % date.today().strftime("%d%m%y")

    if filename not in ftp.nlst():
        raise FileNotFoundError('RCP file not found on WPM FTP server: %s' % filename)

    # Write the file into a buffer
    file = StringIO()
    ftp.retrlines(f"RETR {filename}", lambda line: file.write('%s\n' % line))

    rows_inserted = 0
    fieldnames = ['invoice_no', 'blank_1', 'blank_2', 'name', 'digits', 'card', 'amount', 'trans_id', 'date', 'status']

    # Looping through the file
    csv_file = csv.DictReader(file.getvalue().splitlines(), delimiter=',', fieldnames=fieldnames)
    for row in csv_file:
        # isdigit to filter out non-invoice items (FOLL)
        if row['status'] != 'success' or not row['invoice_no'].isdigit():
            continue

        amount = Decimal(row['amount'])
        if amount > 0:  # Filter out RCP refunds, which will have already been listed in the ledger
            continue

        date = datetime.strptime(row['date'], '%d/%m/%y %H:%M')
        narrative = f"{row['name']}, card: {row['card']}, digits: {row['digits']}, trans: {row['trans_id']}"[:128]
        invoice = Invoice.objects.get(number=row['invoice_no'])

        # todo: implement invoice payment
        # insert_invoice_payment(
        #     invoice.id,
        #     amount,
        #     17,  # RCP
        #     narrative,
        #     date=date
        # )

        # debugging while above not implemented
        print(narrative)

        rows_inserted += 1

    # Todo: Collect together basic payment info and send a summary to finance
    # Todo: Check the failures file and send info to finance

    return f'{filename}: {rows_inserted} payments'
