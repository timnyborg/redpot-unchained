from datetime import date

from django.test import TestCase

from ..models import Module


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
