from rest_framework import status, test

from django.urls import reverse

from apps.core.utils.tests import LoggedInMixin
from apps.module.tests.factories import ModuleFactory

from . import factories


class TestReordering(LoggedInMixin, test.APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.module = ModuleFactory()
        cls.tutors = factories.TutorModuleFactory.create_batch(module=cls.module, size=3)

    def test_ordering(self):
        data = {'ids': [self.tutors[1].pk, self.tutors[0].pk, self.tutors[2].pk]}
        response = self.client.patch(reverse('tutor:module:reorder'), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tutors[0].refresh_from_db()
        self.tutors[1].refresh_from_db()
        self.assertEqual(self.tutors[0].display_order, 1)
        self.assertEqual(self.tutors[1].display_order, 0)
