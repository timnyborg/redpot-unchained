from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Module


class TestViewsWithoutLogin(TestCase):
    def test_views_require_login(self):
        response = self.client.get(reverse('module:search'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('module:edit', args=[1]))
        self.assertEqual(response.status_code, 302)


class TestViewsWithLogin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.object = Module.objects.create(
            title='Test module',
            start_date=date(2000, 1, 1)
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_search_loads(self):
        response = self.client.get(reverse('module:search'))
        self.assertEqual(response.status_code, 200)

    def test_search_limited_years(self):
        # todo: parameterized search testing using subtests or parameterized
        response = self.client.get(reverse('module:search'), data={'limit_years': 'on'})
        table = response.context['table']
        self.assertEqual(len(table.rows), 0)

    def test_search_unlimited_years(self):
        response = self.client.get(reverse('module:search'), data={'limit_years': ''})
        table = response.context['table']
        self.assertEqual(len(table.rows), 1)

    def test_view_page(self):
        response = self.client.get(reverse('module:view', args=[self.object.pk]))
        self.assertEqual(response.status_code, 200)

    def test_edit_page(self):
        response = self.client.get(reverse('module:edit', args=[self.object.pk]))
        self.assertEqual(response.status_code, 200)
