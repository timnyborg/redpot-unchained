from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class TestViewsWithLogin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='test_user')

    def setUp(self):
        self.client.force_login(self.user)

    def test_search_loads(self):
        response = self.client.get(reverse('invoice:search'))
        self.assertEqual(response.status_code, 200)

    def test_search_with_outstanding_filter(self):
        response = self.client.get(reverse('invoice:search'), {'outstanding': 'on'})
        self.assertEqual(response.status_code, 200)

    def test_search_without_filters(self):
        response = self.client.get(reverse('invoice:search'), {
            'invoiced_to': '',
            'minimum': '',
            'maximum': '',
            'created_by': '',
            'created_after': '',
        })
        self.assertEqual(response.status_code, 200)
