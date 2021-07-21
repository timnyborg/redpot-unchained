import ftplib
import io
from datetime import date

from redpot.celery import app
from redpot.settings import WPM_FTP as CONFIG

from . import services


@app.task(name="repeating_card_payment_download")
def repeating_card_payment_download(filename: str = None) -> str:
    """
    Gets today's rcp payment data from WPM via ftp and creates invoice payments
    Can be overridden to download a particular file (e.g. a past date) via `filename`
    """

    # If unspecified, get today's payments file
    filename = filename or 'RCP_Payments_%s.csv' % date.today().strftime("%d%m%y")
    file = _get_file_from_wpm_ftp(filename)
    payments_added = services.add_repeating_payments_from_file(file=file)

    # Todo: Collect together basic payment info and send a summary to finance
    # Todo: Check the failures file and send info to finance

    return f'{filename}: {payments_added} payments'


def _get_file_from_wpm_ftp(filename: str) -> io.BytesIO:
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
    return file
