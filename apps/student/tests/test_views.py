from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Student
from .factories import StudentFactory


class TestViewsWithoutLogin(TestCase):
    def test_views_require_login(self):
        response = self.client.get(reverse('student:search'))
        self.assertEqual(response.status_code, 302)


class TestSearch(TestCase):
    url = reverse('student:search')

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = StudentFactory(
            firstname='Stephen',
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


class TestCreateStudent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = StudentFactory()
        cls.url = reverse('student:new')

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_create_student(self):
        # Do the search, loading the session
        response = self.client.post(
            self.url,
            data={
                'surname': 'smith',
                'firstname': 'steve',
                'email': 'test@test.net',
            },
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            self.url,
            data={'action': 'create'},
        )
        self.assertEqual(response.status_code, 302)
        newest_student = Student.objects.last()
        self.assertEqual(newest_student.surname, 'smith')
        self.assertEqual(newest_student.emails.first().email, 'test@test.net')


class TestCreateEmail(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = StudentFactory()
        cls.url = reverse('student:email-create', kwargs={'student_id': cls.student.pk})
        cls.invalid_url = reverse('student:email-create', kwargs={'student_id': 0})

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_creates_email(self):
        response = self.client.post(
            self.url,
            data={
                'student': self.student.pk,
                'email': 'test@test.net',
                'note': 'An email address!',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.student.emails.first().email, 'test@test.net')

    def test_invalid_student_returns_404(self):
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, 404)
