from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Student


class TestViewsWithoutLogin(TestCase):
    def test_views_require_login(self):
        response = self.client.get(reverse('student:search'))
        self.assertEqual(response.status_code, 302)


class TestSearch(TestCase):
    url = reverse('student:search')

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = Student.objects.create(
            firstname='Stephen',
            surname='Smith',
            nickname='Steve',
        )
        cls.student.emails.create(email='steve@smith.net')
        cls.student.addresses.create(postcode='OX1 2JA')

    def setUp(self):
        self.client.force_login(self.user)

    def test_search_by_nickname(self):
        response = self.client.get(self.url, data={'firstname': 'Steve'})
        self.assertEqual(len(response.context['table'].rows), 1)
        response = self.client.get(self.url, data={'firstname': 'Todd'})
        self.assertEqual(len(response.context['table'].rows), 0)

    def test_search_by_full_email(self):
        response = self.client.get(self.url, data={'email': 'steve@smith.net'})
        self.assertEqual(len(response.context['table'].rows), 1)
        response = self.client.get(self.url, data={'email': 'todd@smith.net'})
        self.assertEqual(len(response.context['table'].rows), 0)

    def test_search_by_partial_email(self):
        response = self.client.get(self.url, data={'email': '@smith.net'})
        self.assertEqual(len(response.context['table'].rows), 1)

    def test_search_by_postcode(self):
        response = self.client.get(self.url, data={'postcode': 'OX1 2JA'})
        self.assertEqual(len(response.context['table'].rows), 1)
        response = self.client.get(self.url, data={'postcode': 'TE1 1ST'})
        self.assertEqual(len(response.context['table'].rows), 0)
