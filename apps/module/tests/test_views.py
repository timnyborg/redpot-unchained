from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class TestViewsWithoutLogin(TestCase):
    def test_views_require_login(self):
        response = self.client.get(reverse('module:search'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('module:edit', args=[1]))
        self.assertEqual(response.status_code, 302)


class TestViewsWithLogin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='test_user')

    def setUp(self):
        self.client.force_login(self.user)

    def test_search(self):
        response = self.client.get(reverse('module:search'))
        self.assertEqual(response.status_code, 200)