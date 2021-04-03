from datetime import date, datetime

from freezegun import freeze_time
from parameterized import parameterized

from django.test import TestCase

from ..models import Module, Statuses


class TestModuleModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.object = Module.objects.create(
            title='Test module',
            url='test-module',
            start_date=date(2020, 1, 1),
        )
        cls.next_run = Module.objects.create(
            title='Test module',
            url='test-module',
            is_published=True,
            start_date=date(2021, 1, 1),
        )

    def test_module_finance_code(self):
        # Check None is returned if lacking pieces
        self.object.cost_centre = 'XA1234'
        self.object.save()
        self.assertIsNone(self.object.finance_code)

        self.object.activity_code = '00'
        self.object.source_of_funds = '12345'
        self.object.save()

        # Check the full string is returned when all parts are set
        self.assertEqual(self.object.finance_code, 'XA1234 00 12345')

    def test_other_runs(self):
        self.assertIn(self.next_run, self.object.other_runs())

    def test_next_run(self):
        self.assertEqual(self.next_run, self.object.next_run())


class TestUpdateModuleStatus(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.object = Module.objects.create(
            title='Test module',
            url='test-module',
            auto_publish=True,
            publish_date=date(2020, 2, 1),
            open_date=date(2020, 3, 1),
            start_date=date(2020, 4, 1),
            closed_date=datetime(2020, 5, 1),
            end_date=date(2020, 6, 1),
            unpublish_date=date(2020, 7, 1),
        )

    @parameterized.expand(
        [
            ('unpublished', "2020-01-01", Statuses.UNPUBLISHED),
            ('not_yet_open', "2020-02-01", Statuses.NOT_YET_OPEN),
            ('open', "2020-03-01", Statuses.OPEN),
            ('running_and_open', "2020-04-01", Statuses.RUNNING_AND_OPEN),
            ('running_and_closed', "2020-05-01", Statuses.RUNNING_AND_CLOSED),
            ('lastday', "2020-06-01", Statuses.RUNNING_AND_CLOSED),
            ('ended', "2020-06-02", Statuses.ENDED),
            ('unpublished', "2020-07-01", Statuses.UNPUBLISHED),
        ]
    )
    def test_publish(self, _, now, expected):
        # todo: pare this down to use _get_auto_status() and a bare Module() once update_status() is tested separately
        with freeze_time(now):
            self.object.update_status()
            self.assertEqual(self.object.status_id, expected)
