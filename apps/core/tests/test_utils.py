from contextlib import suppress
from datetime import date

import django_tables2 as tables
from parameterized import parameterized

from django import http
from django.core import mail
from django.test import RequestFactory, SimpleTestCase

from ..utils import celery, datatables, dates, urls, widgets


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


class TestMailOnFailure(SimpleTestCase):
    @celery.mail_on_failure
    def fails(self):
        raise Exception()

    def test_mail_on_failure(self):
        with suppress(Exception):
            self.fails()
        # Check mail was sent
        self.assertEqual(len(mail.outbox), 1)


class TestMonthPickerWidget(SimpleTestCase):
    widget = widgets.MonthPickerInput()

    def test_adds_day(self):
        result = self.widget.value_from_datadict(
            data={'name': 'January 2021'},
            files={},
            name='name',
        )
        self.assertEqual(result, date(2021, 1, 1))

    def test_ignores_nondate(self):
        result = self.widget.value_from_datadict(
            data={'name': 'garbage'},
            files={},
            name='name',
        )
        self.assertEqual(result, 'garbage')

    def test_handles_no_data(self):
        result = self.widget.value_from_datadict(
            data={},
            files={},
            name='name',
        )
        self.assertIsNone(result)


class TestNextURLIfSafe(SimpleTestCase):
    @parameterized.expand(
        [
            ('valid', '/next/page', '/next/page'),
            ('invalid', 'https://google.com', None),
            ('empty', None, None),
        ]
    )
    def test_url(self, _, url, expected):
        request = http.HttpRequest()
        request.GET['next'] = url
        self.assertEqual(urls.next_url_if_safe(request), expected)
