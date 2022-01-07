import io
from datetime import date

import paramiko

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
    filename = filename or f'RCP_Payments_{date.today():%d%m%y}.csv'
    file = _get_file_from_wpm_sftp(filename)
    payments_added = services.add_repeating_payments_from_file(file=file)

    # Todo: Collect together basic payment info and send a summary to finance
    # Todo: Check the failures file and send info to finance

    return f'{filename}: {payments_added} payments'


def _get_file_from_wpm_sftp(filename: str) -> io.BytesIO:
    """Log into the WPM sftp and download a given RCP result file
    Opens a connection over SSH, then uses it for an SFTP session.
    """
    with paramiko.SSHClient() as client:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        client.connect(hostname=CONFIG['HOST'], username=CONFIG['USER'], password=CONFIG['PASSWORD'])

        with client.open_sftp() as sftp:
            sftp.chdir(CONFIG['DIRECTORY'])

            if filename not in sftp.listdir():
                raise FileNotFoundError(f'RCP file not found on WPM SFTP server: {filename}')

            file = io.BytesIO()
            sftp.getfo(remotepath=filename, fl=file)
            file.seek(0)
            return file
