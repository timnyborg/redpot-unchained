from unittest.mock import patch, ANY

from django.test import TestCase

from ..tasks import wpm_ftp_download


class TestWPMDownload(TestCase):
    @patch('ftplib.FTP_TLS', autospec=True)
    def test_retrieves_correct_file(self, mock_class):
        filename = 'test.csv'

        # Patch the returned object's nlst() method so the file appears available
        mock_ftp_obj = mock_class()
        mock_ftp_obj.nlst.return_value = [filename]

        wpm_ftp_download(filename)
        # Check that RETR was called
        mock_ftp_obj.retrlines.assert_called_with(f"RETR {filename}", ANY)

    @patch('ftplib.FTP_TLS', autospec=True)
    def test_missing_file_error(self, mock_class):
        # Patch the returned object's nlst() method so the file appears unavailable
        mock_ftp_obj = mock_class()
        mock_ftp_obj.nlst.return_value = ['other.csv']

        with self.assertRaises(FileNotFoundError):
            wpm_ftp_download('missing.csv')

    # todo: test parsing and db methods
