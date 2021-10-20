from unittest.mock import patch
from uuid import uuid4

from django import test
from django.urls import reverse

from apps.core.utils.tests import LoggedInViewTestMixin


class TestCreateBatch(LoggedInViewTestMixin, test.TestCase):
    url = reverse('hesa:new-batch')
    superuser = True

    @patch('apps.hesa.tasks.create_return')
    def test_post(self, mock_method):
        """Check that the view queues a return"""
        mock_method.delay.return_value.id = uuid4()  # Fake a celery task id
        response = self.client.post(self.url, {'year': 2010})
        self.assertTrue(mock_method.delay.called_with(year=2010))
        self.assertEqual(response.status_code, 302)
