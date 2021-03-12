from datetime import date, datetime

from django.test import SimpleTestCase

from apps.core.utils.dates import academic_year


class TestAcademicYear(SimpleTestCase):
    def test_beginning_of_year(self):
        self.assertEqual(academic_year(date(2020, 8, 1)), 2020)

    def test_end_of_year(self):
        self.assertEqual(academic_year(date(2020, 7, 31)), 2019)

    def test_default(self):
        self.assertIsInstance(academic_year(), int)
