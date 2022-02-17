from unittest import mock

from django import test
from django.urls import reverse

from apps.core.tests.factories import UserFactory
from apps.core.utils.tests import LoggedInMixin, LoggedInViewTestMixin


class TestNewView(LoggedInViewTestMixin, test.TestCase):
    superuser = True
    url = reverse('user:new')

    @mock.patch('django_auth_ldap.backend.LDAPBackend')
    def test_tries_ldap_creation(self, mock_class: mock.MagicMock):
        instance = mock_class.return_value
        instance.populate_user.return_value = None  # ldap couldn't find a user

        self.client.post(self.url, data={'username': 'test'})

        instance.populate_user.assert_called_with('test')


class TestEditView(LoggedInMixin, test.TestCase):
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.other_user = UserFactory()

    def test_own_profile(self):
        response = self.client.get(reverse('user:edit'))
        self.assertEqual(response.context['user'], self.user)

    def test_other_profile(self):
        response = self.client.get(reverse('user:edit', kwargs={'pk': self.other_user.pk}))
        self.assertEqual(response.context['user'], self.other_user)
