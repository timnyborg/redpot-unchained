from unittest.mock import patch

from django import test

from .. import tasks


class TestCreateReturnTask(test.SimpleTestCase):
    """Check that the task calls the service layer"""

    @patch('apps.hesa.tasks.ProgressRecorder')
    @patch('apps.hesa.services.save_xml')
    @patch('apps.hesa.services.create_return')
    def test_calls_service(self, create_return, save_xml, _):
        create_return.return_value.pk = 1  # for url
        tasks.create_return(academic_year=2020, created_by='test')
        self.assertTrue(create_return.called)
        self.assertTrue(save_xml.called)
