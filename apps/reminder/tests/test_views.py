from django import test
from django.urls import reverse

from apps.core.utils.tests import LoggedInViewTestMixin
from apps.module.tests.factories import ModuleFactory


class TestPreview(LoggedInViewTestMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.module = ModuleFactory()
        cls.url = reverse('reminder:preview', kwargs={'pk': cls.module.pk})

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This is a reminder')
