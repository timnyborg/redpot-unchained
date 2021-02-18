from django.test import TestCase
from django.urls import reverse

from apps.module.models import Module


class TestModuleAutocomplete(TestCase):
    @classmethod
    def setUpTestData(cls):
        Module.objects.create(
            code='T12T123TTT',
            title='The Brontës'
        )

    def test_search_by_code(self):
        response = self.client.get(reverse('autocomplete:module'), {'q': '2T12'})
        self.assertIn('The Brontës', response)

    def test_search_by_title_with_accent(self):
        response = self.client.get(reverse('autocomplete:module'), {'q': 'Bronte'})
        self.assertIn('The Brontës', response)

    def test_search_without_match(self):
        response = self.client.get(reverse('autocomplete:module'), {'q': 'Durer'})
        self.assertNotIn('The Brontës', response)
