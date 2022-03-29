from datetime import date

from django import test
from django.core import mail
from django.urls import reverse

from apps.core.utils.tests import LoggedInMixin, LoggedInViewTestMixin
from apps.module.tests.factories import ModuleFactory
from apps.student.tests.factories import EmailFactory, StudentFactory

from ..models import Waitlist


class TestAdd(LoggedInViewTestMixin, test.TestCase):
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


class TestDelete(LoggedInMixin, test.TestCase):
    def test_delete(self):
        waitlist = Waitlist.objects.create(student=StudentFactory(), module=ModuleFactory())
        response = self.client.post(waitlist.get_delete_url())
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Waitlist.DoesNotExist):
            waitlist.refresh_from_db()


class TestEmailViews(LoggedInMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Put two students with an email address on a waitlist
        cls.module, cls.new_run = ModuleFactory.create_batch(start_date=date(2020, 1, 1), size=2)
        cls.waitlist = Waitlist.objects.create(module=cls.module, student=StudentFactory())
        cls.email = EmailFactory(student=cls.waitlist.student)
        cls.waitlist_2 = Waitlist.objects.create(module=cls.module, student=StudentFactory())
        cls.email_2 = EmailFactory(student=cls.waitlist_2.student)

    def test_email_single(self):
        response = self.client.get(reverse('waitlist:email-single', kwargs={'pk': self.waitlist.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, [self.user.email])
        self.assertIn(self.email.email, email.body)
        self.assertIn(self.module.title, email.body)

    def test_email_multiple_with_new_module(self):
        response = self.client.get(
            reverse('waitlist:email-multiple', kwargs={'module': self.new_run.id, 'previous_module': self.module.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, [self.user.email])
        # should contain both email addresses
        self.assertIn(self.email.email, email.body)
        self.assertIn(self.email_2.email, email.body)
        self.assertIn(self.new_run.title, email.body)

    def test_email_multiple_limited(self):
        response = self.client.get(
            reverse('waitlist:email-multiple', kwargs={'module': self.module.id}),
            data={'limited': True, 'id': [self.waitlist.id]},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, [self.user.email])
        self.assertIn(self.module.title, email.body)
        # should not contain both email addresses
        self.assertIn(self.email.email, email.body)
        self.assertNotIn(self.email_2.email, email.body)
