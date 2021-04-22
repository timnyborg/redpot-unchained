from unittest.mock import ANY, patch

from django.test import TestCase

from ..tasks import repeating_card_payment_download


class TestWPMDownload(TestCase):
    @patch('ftplib.FTP_TLS', autospec=True)
    def test_retrieves_correct_file(self, mock_class):
        filename = 'test.csv'

        # Patch the returned object's nlst() method so the file appears available
        mock_ftp_obj = mock_class()
        mock_ftp_obj.nlst.return_value = [filename]

        repeating_card_payment_download(filename)
        # Check that RETR was called
        mock_ftp_obj.retrbinary.assert_called_with(f"RETR {filename}", ANY)

    @patch('ftplib.FTP_TLS', autospec=True)
    def test_missing_file_error(self, mock_class):
        # Patch the returned object's nlst() method so the file appears unavailable
        mock_ftp_obj = mock_class()
        mock_ftp_obj.nlst.return_value = ['other.csv']

        with self.assertRaises(FileNotFoundError):
            repeating_card_payment_download('missing.csv')

    # todo: test parsing and db methods
