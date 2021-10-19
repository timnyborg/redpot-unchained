from django import test
from django.core import mail

from apps.contract import services
from apps.contract.tests.factories import ContractFactory
from apps.core.utils.tests import LoggedInMixin


class TestTutorPendingEmailContract(LoggedInMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.contract = ContractFactory()

    def test_send_contract_email(self):
        # Send message
        services.mail_pending_contracts_signature()

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Tutor contracts awaiting signature')
