from django import test
from django.core import mail

from apps.core.tests.factories import UserFactory

from .. import tasks
from . import factories


class TestPendingTutorPaymentsEmail(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.approver = UserFactory()

    def test_email_sent(self):
        factories.PaymentFactory.create_batch(approver=self.approver, size=3)

        result = tasks.mail_pending_tutor_payments()

        self.assertEqual(result, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('3 tutor payments', mail.outbox[0].body)
