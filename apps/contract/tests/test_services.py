from django.core import mail
from django.test import TestCase, override_settings

from apps.contract import services
from apps.contract.tests.factories import ContractFactory
from apps.core.utils.tests import LoggedInMixin


@override_settings(DEFAULT_FROM_EMAIL='test@test.com')
class TestTutorPendingEmailContract(LoggedInMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.contract = ContractFactory()

    def test_send_contract_email(self):
        # Send message
        services.mail_pending_contracts_signature()

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Tutor contracts awaiting signature')
        self.assertEqual(mail.outbox[0].from_email, 'test@test.com')

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)
