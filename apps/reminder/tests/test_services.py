from itertools import chain

from django import test
from django.core import mail

from apps.enrolment.models import Statuses
from apps.enrolment.tests.factories import EnrolmentFactory
from apps.module.tests.factories import ModuleFactory
from apps.student.tests.factories import EmailFactory

from .. import services


class TestRenderingMessage(test.SimpleTestCase):
    def test_standard_message(self):
        module = ModuleFactory.build()
        message = services.render_reminder(module=module, first_name='Steve')
        self.assertIn('Steve', message)
        self.assertIn(module.title, message)
        self.assertNotIn('course demonstration site', message)

    def test_short_online_message(self):
        module = ModuleFactory.build(portfolio_id=services.SHORT_ONLINE_PORTFOLIO)
        message = services.render_reminder(module=module, first_name='Steve')
        self.assertIn('Steve', message)
        self.assertIn(module.title, message)
        self.assertIn('course demonstration site', message)


class TestSendingReminders(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.module = ModuleFactory(email='test@conted.ox.ac.uk')

    def test_emails_confirmed_student(self):
        enrolment = EnrolmentFactory(module=self.module, status_id=Statuses.CONFIRMED)
        email = EmailFactory(student=enrolment.qa.student)
        services.mail_module_reminders(module=self.module)
        self.assertEqual(len(mail.outbox), 2)  # 1 + admin
        self.assertEqual(
            # Check it emails both the admin and the student
            set(chain.from_iterable(item.recipients() for item in mail.outbox)),
            {self.module.email, email.email},
        )
        self.assertIsNotNone(self.module.reminder_sent_on)

    def test_does_not_email_unconfirmed_student(self):
        enrolment = EnrolmentFactory(module=self.module, status_id=Statuses.WITHDRAWN_UP_TO_3_WEEKS)
        email = EmailFactory(student=enrolment.qa.student)
        services.mail_module_reminders(module=self.module)
        self.assertEqual(len(mail.outbox), 1)  # 0 + admin
        self.assertNotIn(email.email, mail.outbox[0].recipients())

    def test_ignores_students_without_email(self):
        EnrolmentFactory(module=self.module, status_id=Statuses.CONFIRMED)
        services.mail_module_reminders(module=self.module)
        self.assertEqual(len(mail.outbox), 1)  # 0 + admin
