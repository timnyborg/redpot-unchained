from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Module
from . import factories


class TestViewsWithoutLogin(TestCase):
    def test_views_require_login(self):
        response = self.client.get(reverse('module:search'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('module:edit', args=[1]))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('module:toggle-auto-reminder', args=[1]))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('module:toggle-auto-feedback', args=[1]))
        self.assertEqual(response.status_code, 302)


class TestViewsWithLogin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.object = Module.objects.create(
            title='Test module',
            start_date=date(2000, 1, 1),
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

    def test_toggle_autoreminder(self):
        """Test that auto_reminder is toggled from True -> False, then False -> True"""
        response = self.client.post(reverse('module:toggle-auto-reminder', args=[self.object.pk]))
        self.assertEqual(response.status_code, 200)
        self.object.refresh_from_db()
        self.assertEqual(self.object.auto_reminder, False)

        response = self.client.post(reverse('module:toggle-auto-reminder', args=[self.object.pk]))
        self.assertEqual(response.status_code, 200)
        self.object.refresh_from_db()
        self.assertEqual(self.object.auto_reminder, True)

    def test_toggle_autofeedback(self):
        """Test that auto_feedback is toggled from True -> False, then False -> True"""
        response = self.client.post(reverse('module:toggle-auto-feedback', args=[self.object.pk]))
        self.assertEqual(response.status_code, 200)
        self.object.refresh_from_db()
        self.assertEqual(self.object.auto_feedback, False)

        response = self.client.post(reverse('module:toggle-auto-feedback', args=[self.object.pk]))
        self.assertEqual(response.status_code, 200)
        self.object.refresh_from_db()
        self.assertEqual(self.object.auto_feedback, True)

    def test_new_page_get(self):
        response = self.client.get(reverse('module:new'))
        self.assertEqual(response.status_code, 200)

    def test_new_page_post(self):
        response = self.client.post(
            reverse('module:new'),
            data={'code': 'T12T123TTT', 'title': 'Test', 'division': 1, 'portfolio': 1, 'non_credit_bearing': True},
        )
        # Check that we've been forwarded, and the new module was created
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Module.objects.last().code, 'T12T123TTT')


class TestCloneView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.object = factories.ModuleFactory()
        cls.url = reverse('module:clone', args=[cls.object.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_clone(self):
        response = self.client.post(
            self.url,
            data={
                'title': 'New title',
                'code': 'T99T123TTT',
                'keep_url': True,
                'copy_fees': True,
                'copy_dates': False,
            },
        )
        self.assertEqual(response.status_code, 302)
        new_module = Module.objects.last()

        self.assertEqual(new_module.url, self.object.url)
        self.assertEqual(new_module.title, 'New title')
        self.assertIsNone(new_module.start_date)
