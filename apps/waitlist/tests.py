from django import test
from django.urls import reverse

from apps.core.utils.tests import LoggedInMixin, LoggedInViewTestMixin
from apps.module.tests.factories import ModuleFactory
from apps.student.tests.factories import StudentFactory
from apps.waitlist.models import Waitlist


class TestAddView(LoggedInViewTestMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.module = ModuleFactory()
        cls.student = StudentFactory()
        cls.url = reverse('waitlist:add', kwargs={'student_id': cls.student.id})

    def test_post(self):
        response = self.client.post(self.url, data={'student': self.student.id, 'module': self.module.id})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Waitlist.objects.last().student, self.student)


class TestDeleteView(LoggedInMixin, test.TestCase):
    def test_delete(self):
        waitlist = Waitlist.objects.create(student=StudentFactory(), module=ModuleFactory())
        response = self.client.post(waitlist.get_delete_url())
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Waitlist.DoesNotExist):
            waitlist.refresh_from_db()
