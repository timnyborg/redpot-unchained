from unittest import mock

from django import test
from django.urls import reverse

from apps.core.utils.tests import LoggedInViewTestMixin


class TestNewView(LoggedInViewTestMixin, test.TestCase):
    superuser = True
    url = reverse('user:new')

    @mock.patch('django_auth_ldap.backend.LDAPBackend')
    def test_tries_ldap_creation(self, mock_class: mock.MagicMock):
        instance = mock_class.return_value
        instance.populate_user.return_value = None  # ldap couldn't find a user

        self.client.post(self.url, data={'username': 'test'})

        instance.populate_user.assert_called_with('test')
