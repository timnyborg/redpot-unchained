from unittest.mock import ANY, patch

from django.test import TestCase

from ..tasks import repeating_card_payment_download


@patch('paramiko.SSHClient', autospec=True)
class TestWPMDownload(TestCase):
    # awkward mocking chains with __enter__ due to nested context managers in the routine
    def test_retrieves_correct_file(self, mock_class):
        filename = 'test.csv'

        # Patch the returned object's listdir() method so the file appears available
        mock_ftp_obj = mock_class()
        mock_ftp_obj.__enter__().open_sftp().__enter__().listdir.return_value = [filename]
        repeating_card_payment_download(filename)
        mock_ftp_obj.__enter__().open_sftp().__enter__().getfo.assert_called_with(fl=ANY, remotepath=filename)

    def test_missing_file_error(self, mock_class):
        # Patch the returned object's listdir() method so the file appears unavailable
        mock_class().__enter__().open_sftp().__enter__().listdir.return_value = ['other.csv']

        with self.assertRaises(FileNotFoundError):
            repeating_card_payment_download('missing.csv')

    # todo: test parsing and db methods
