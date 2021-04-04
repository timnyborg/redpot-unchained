from datetime import date

import django_tables2 as tables

from django.test import RequestFactory, SimpleTestCase

from ..utils import datatables, dates


class TestAcademicYear(SimpleTestCase):
    def test_beginning_of_year(self):
        self.assertEqual(dates.academic_year(date(2020, 8, 1)), 2020)

    def test_end_of_year(self):
        self.assertEqual(dates.academic_year(date(2020, 7, 31)), 2019)

    def test_default(self):
        self.assertIsInstance(dates.academic_year(), int)


class TestLinkColumns(SimpleTestCase):
    """Check that our custom link columns access the correct properties on an object"""

    class Dummy:
        id = 1

        def get_absolute_url(self):
            return '/view/'

        def get_edit_url(self):
            return '/edit/'

        def get_delete_url(self):
            return '/delete/'

    def setUp(self):
        self.factory = RequestFactory()
        self.obj = self.Dummy()

    def test_view_link(self):
        class LinkTable(tables.Table):
            link = datatables.ViewLinkColumn('')

        request = self.factory.get('')
        html = LinkTable(data=[self.obj]).as_html(request)
        self.assertIn('<a href="/view/">', html)

    def test_edit_link(self):
        class LinkTable(tables.Table):
            link = datatables.EditLinkColumn('')

        request = self.factory.get('')
        html = LinkTable(data=[self.obj]).as_html(request)
        self.assertIn('<a href="/edit/">', html)

    def test_delete_link(self):
        class LinkTable(tables.Table):
            link = datatables.DeleteLinkColumn('')

        request = self.factory.get('')
        html = LinkTable(data=[self.obj]).as_html(request)
        self.assertIn('<a href="/delete/">', html)
