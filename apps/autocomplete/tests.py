from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.module.tests.factories import ModuleFactory
from apps.student.tests.factories import StudentFactory
from apps.tutor.tests.factories import TutorFactory


class TestModuleAutocomplete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        ModuleFactory(code='T12T123TTT', title='The Brontës')
        cls.url = reverse('autocomplete:module')

    def setUp(self):
        self.client.force_login(self.user)

    def test_search_by_code(self):
        response = self.client.get(self.url, {'q': '2T12'})
        self.assertContains(response, 'The Bront')

    def test_search_by_title_with_accent(self):
        response = self.client.get(self.url, {'q': 'Bronte'})
        self.assertContains(response, 'The Bront')

    def test_search_without_match(self):
        response = self.client.get(self.url, {'q': 'Durer'})
        self.assertNotContains(response, 'The Bront')


class TestTutorAutocomplete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        student = StudentFactory(firstname='João', surname='Český')
        TutorFactory(student=student)
        cls.url = reverse('autocomplete:tutor')

    def setUp(self):
        self.client.force_login(self.user)

    def test_search_by_firstname_with_accent(self):
        response = self.client.get(self.url, {'q': 'João'})
        self.assertContains(response, 'Jo')

    def test_search_by_surname_with_accent(self):
        response = self.client.get(self.url, {'q': 'Český'})
        self.assertContains(response, 'Jo')

    def test_search_without_match(self):
        response = self.client.get(self.url, {'q': 'Sam'})
        self.assertNotContains(response, 'Jo')
