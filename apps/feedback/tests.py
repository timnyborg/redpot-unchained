from django import test
from django.core import mail
from django.urls import reverse

from apps.core.utils.tests import LoggedInMixin
from apps.enrolment.tests.factories import EnrolmentFactory
from apps.student.tests.factories import EmailFactory

from . import models


class TestEmailing(LoggedInMixin, test.TestCase):
    def test_several_things(self):
        # Create an enrolment on a module eligible for feedback
        enrolment = EnrolmentFactory(module__email='fake@conted.ox.ac.uk', module__auto_feedback=True)
        EmailFactory(student=enrolment.qa.student, email='test@test.net', is_default=True)

        url = reverse('feedback:request-feedback', args=[enrolment.module.pk])

        # Check the first posting creates feedback, sends an email
        self.client.post(url)

        self.assertEqual(models.Feedback.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(enrolment.qa.student.firstname, mail.outbox[0].body)
        self.assertIsNone(models.Feedback.objects.first().reminder)

        # Check the second posting sets the reminder, sends an email
        self.client.post(url)

        self.assertEqual(models.Feedback.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)
        self.assertIsNotNone(models.Feedback.objects.first().reminder)

        # Check the third posting does nothing
        self.client.post(url)

        self.assertEqual(models.Feedback.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)
