from django.core import mail
from django.test import TestCase, override_settings

from apps.contract import services
from apps.contract.tests.factories import ContractFactory


@override_settings(DEFAULT_FROM_EMAIL='test@test.com')
class TestTutorPendingEmailContract(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.contract = ContractFactory()

    def test_send_contract_email(self):
        # Send message
        services.mail_pending_contracts_signature()

        # Verify that the subject of the first message is correct.
        self.assertIn('Tutor contracts awaiting signature', mail.outbox[0].subject)
        self.assertIn('test@test.com', mail.outbox[0].from_email)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)
