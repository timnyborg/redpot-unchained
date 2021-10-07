from django.test import TestCase
from django.urls import reverse, reverse_lazy

from . import factories


class TestViewsWithoutLogin(TestCase):
    def test_homepage(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


class TestImpersonate(TestCase):
    url = reverse_lazy('impersonate')

    def test_non_superuser_cannot_access(self):
        regular_user = factories.UserFactory(is_superuser=False, is_staff=True)
        self.client.force_login(regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_access(self):
        regular_user = factories.UserFactory(is_superuser=True, is_staff=True)
        self.client.force_login(regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
