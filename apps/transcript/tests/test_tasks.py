from datetime import date
from unittest import mock

from django import test

from apps.enrolment.models import Results, Statuses
from apps.enrolment.tests.factories import EnrolmentFactory

from .. import tasks


class TestCreateBatch(test.TestCase):
    @mock.patch('apps.transcript.tasks.ProgressRecorder')
    def test_create_undergraduate(self, mock_recorder_class):
        EnrolmentFactory(
            qa__programme__qualification_id=61,
            status_id=Statuses.CONFIRMED,
            result_id=Results.PASSED,
            points_awarded=10,
            module__credit_points=10,
            module__start_date=date(2020, 1, 1),
            module__end_date=date(2020, 1, 1),
            module__points_level_id=1,  # UG
        )
        tasks.create_batch(level='undergraduate', header=True, created_by='test')
        self.assertTrue(mock_recorder_class.called)
