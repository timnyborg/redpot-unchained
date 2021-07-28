from unittest.mock import patch

from django import test

from .. import tasks


class TestCreateReturnTask(test.SimpleTestCase):
    """Check that the task calls the service layer"""

    @patch('apps.hesa.services.create_return')
    def test_calls_service(self, mock_method):
        tasks.create_return(academic_year=2020, created_by='test')
        self.assertTrue(mock_method.called)
