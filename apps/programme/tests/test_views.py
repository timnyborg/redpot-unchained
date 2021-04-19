from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.module.tests.factories import ModuleFactory

from .factories import ProgrammeFactory


class TestViewsWithoutLogin(TestCase):
    def test_views_require_login(self):
        response = self.client.get(reverse('programme:search'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('programme:edit', args=[1]))
        self.assertEqual(response.status_code, 302)


class TestViewsWithLogin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.object = ProgrammeFactory()
        cls.module = ModuleFactory()

    def setUp(self):
        self.client.force_login(self.user)

    def test_search_loads(self):
        response = self.client.get(reverse('programme:search'))
        self.assertEqual(response.status_code, 200)

    def test_search_with_inactive_filter(self):
        response = self.client.get(reverse('programme:search'), {'show_inactive_filter': 'on'})
        self.assertEqual(response.status_code, 200)

    def test_search_without_inactive_filter(self):
        response = self.client.get(
            reverse('programme:search'),
            {
                'title__icontains': 'on',
                'division': '',
                'portfolio': '',
                'qualification': '',
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_view_page(self):
        response = self.client.get(reverse('programme:view', args=[self.object.pk]))
        self.assertEqual(response.status_code, 200)

    def test_edit_page(self):
        response = self.client.get(reverse('programme:edit', args=[self.object.pk]))
        self.assertEqual(response.status_code, 200)

    def test_add_module(self):
        response = self.client.post(
            reverse('programme:add-module', args=[self.object.pk]),
            data={'module': self.module.pk},
        )
        # Redirects on success
        self.assertEqual(response.status_code, 302)

    def test_new(self):
        response = self.client.post(
            reverse('programme:new'),
            data={
                'title': 'Test programme',
                'qualification': 1,
                'division': 1,
                'sits_code': 'TE_ST',
                'portfolio': 1,
            },
        )
        # Redirects on success
        self.assertEqual(response.status_code, 302)
