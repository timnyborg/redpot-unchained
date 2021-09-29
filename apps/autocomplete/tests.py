from django.test import TestCase
from django.urls import reverse

from apps.core.utils.tests import LoggedInMixin
from apps.module.tests.factories import ModuleFactory
from apps.student.tests.factories import StudentFactory
from apps.tutor.tests.factories import TutorFactory


class TestModuleAutocomplete(LoggedInMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ModuleFactory(code='T12T123TTT', title='The Brontës')
        cls.url = reverse('autocomplete:module')

    def test_search_by_code(self):
        response = self.client.get(self.url, {'q': '2T12'})
        self.assertContains(response, 'The Bront')

    def test_search_by_title_with_accent(self):
        response = self.client.get(self.url, {'q': 'Bronte'})
        self.assertContains(response, 'The Bront')

    def test_search_without_match(self):
        response = self.client.get(self.url, {'q': 'Durer'})
        self.assertNotContains(response, 'The Bront')


class TestTutorAutocomplete(LoggedInMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        student = StudentFactory(firstname='João', surname='Český')
        TutorFactory(student=student)
        cls.url = reverse('autocomplete:tutor')

    def test_search_by_firstname_with_accent(self):
        response = self.client.get(self.url, {'q': 'João'})
        self.assertContains(response, 'Jo')

    def test_search_by_surname_with_accent(self):
        response = self.client.get(self.url, {'q': 'Český'})
        self.assertContains(response, 'Jo')

    def test_search_without_match(self):
        response = self.client.get(self.url, {'q': 'Sam'})
        self.assertNotContains(response, 'Jo')
