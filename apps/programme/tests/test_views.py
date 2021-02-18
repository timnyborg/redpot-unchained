from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Programme
from apps.module.models import Module


class TestViewsWithoutLogin(TestCase):
    def test_views_require_login(self):
        response = self.client.get(reverse('programme:search'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('programme:edit', args=[1]))
        self.assertEqual(response.status_code, 302)


class TestViewsWithLogin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='test_user')
        cls.object = Programme.objects.create(
            title='Test programme',
            division_id=1,
            portfolio_id=1,
            qualification_id=1
        )
        cls.module = Module.objects.create(
            code='O12T123TTT',
            title='Test module'
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_search_loads(self):
        response = self.client.get(reverse('programme:search'))
        self.assertEqual(response.status_code, 200)

    def test_search_with_inactive_filter(self):
        response = self.client.get(reverse('programme:search'), {'show_inactive_filter': 'on'})
        self.assertEqual(response.status_code, 200)

    def test_search_without_inactive_filter(self):
        response = self.client.get(reverse('programme:search'), {
            'title__icontains': 'on',
            'division': '',
            'portfolio': '',
            'qualification': '',
        })
        self.assertEqual(response.status_code, 200)

    def test_view_page(self):
        response = self.client.get(reverse('programme:view', args=[self.object.pk]))
        self.assertEqual(response.status_code, 200)

    def test_edit_page(self):
        response = self.client.get(reverse('programme:edit', args=[self.object.pk]))
        self.assertEqual(response.status_code, 200)

    def test_add_module(self):
        import json
        response = self.client.post(
            reverse('programme:add-module', args=[self.object.pk]),
            data={'module': self.module.pk},
        )
        # Redirects on success
        self.assertEqual(response.status_code, 302)
