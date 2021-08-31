from decimal import Decimal

from parameterized import parameterized

from django import test
from django.core import mail

from apps.core.tests.factories import UserFactory
from apps.enrolment.tests.factories import EnrolmentFactory
from apps.module.tests.factories import ModuleFactory

from .. import models, services
from . import factories


class TestGetNarrative(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.amendment = factories.AmendmentFactory()

    @parameterized.expand(
        [
            ('write-off', models.AmendmentTypes.AMENDMENT),
            ('cc', models.AmendmentTypes.CREDIT_CARD_REFUND),
            ('other', models.AmendmentTypes.OTHER_REFUND),
            ('bank', models.AmendmentTypes.BANK_REFUND),
            ('rcp', models.AmendmentTypes.RCP_REFUND),
        ]
    )
    def test_narratives(self, name: str, type_id: int):
        self.amendment.type_id = type_id
        narrative = services.get_narrative(amendment=self.amendment)
        self.assertIn(str(self.amendment.reason), narrative)

    def test_transfer_to_another_module(self):
        self.amendment.type_id = models.AmendmentTypes.TRANSFER
        target = ModuleFactory()
        self.amendment.transfer_module = target.id
        narrative = services.get_narrative(amendment=self.amendment)
        self.assertIn(target.code, narrative)

    def test_transfer_to_multiple(self):
        self.amendment.type_id = models.AmendmentTypes.TRANSFER
        self.amendment.transfer_module = 'multiple'
        narrative = services.get_narrative(amendment=self.amendment)
        self.assertIn('multiple', narrative)

    def test_transfer_to_another_student(self):
        self.amendment.type_id = models.AmendmentTypes.TRANSFER
        self.amendment.transfer_enrolment = EnrolmentFactory()
        narrative = services.get_narrative(amendment=self.amendment)
        self.assertIn(str(self.amendment.enrolment.qa.student), narrative)


class TestApproveAmendments(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.approver = UserFactory()
        cls.amendments = factories.AmendmentFactory.create_batch(approver=cls.approver, size=2)

    def test_approve(self):
        """Check that the amendments are approved and emails are sent"""
        result = services.approve_amendments(
            amendment_ids=[amendment.id for amendment in self.amendments], username=self.approver.username
        )
        self.assertEqual(result, len(self.amendments))
        self.amendments[0].refresh_from_db()
        self.assertEqual(self.amendments[0].status_id, models.AmendmentStatuses.APPROVED)
        self.assertEqual(len(mail.outbox), len(self.amendments))

    def test_no_id_matches(self):
        """Check that 0 is returned with invalid ids"""
        result = services.approve_amendments(
            amendment_ids=[12345, 56789],
            username=self.approver.username,
        )
        self.assertEqual(result, 0)

    def test_no_approver_matches(self):
        """Check that 0 is returned with the wrong approver"""
        result = services.approve_amendments(
            amendment_ids=[amendment.id for amendment in self.amendments],
            username='someone else',
        )
        self.assertEqual(result, 0)


class TestEmails(test.TestCase):
    """Test that the auto-emails render without error and email the correct recipient"""

    @classmethod
    def setUpTestData(cls):
        cls.amendment = factories.AmendmentFactory(approver=UserFactory())

    def test_create_email(self):
        services.send_request_created_email(amendment=self.amendment)
        self.assertIn(self.amendment.approver.email, mail.outbox[0].to)

    def test_approve_email(self):
        services.send_request_approved_email(amendment=self.amendment)
        self.assertIn(self.amendment.requested_by.email, mail.outbox[0].to)

    def test_complete_email(self):
        services.send_request_complete_email(amendment=self.amendment)
        self.assertIn(self.amendment.requested_by.email, mail.outbox[0].to)


class TestApplyOnlineRefund(test.TestCase):
    """Check that the refund routine applies the right adjustments"""

    def test_enrolment_refunded(self):
        amendment = factories.AmendmentFactory(amount=Decimal(100))
        services.apply_online_refund(amendment=amendment, user=amendment.requested_by)
        amendment.enrolment.refresh_from_db()
        # Check that the balance is unchanged, but payments have shifted £100
        self.assertEqual(amendment.enrolment.get_balance(), Decimal(0))
        self.assertEqual(amendment.enrolment.ledger_set.cash().debts().total(), Decimal(100))
