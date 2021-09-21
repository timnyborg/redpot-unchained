from unittest.mock import patch

from django import test
from django.contrib.auth import get_user_model

from .. import models, services
from . import factories


@patch('apps.tutor_payment.models.TutorFee.approvable', return_value=True)  # We only want to test approvable fees
class TestApprovePayments(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        # begin with an approvable payment
        cls.payment = factories.TutorFeeFactory(
            status_id=models.Statuses.RAISED, raised_by=cls.user, approver=cls.user
        )

    def test_approval(self, patched_method):
        result = services.approve_payments(payment_ids=[self.payment.id], username=self.user.username)
        self.assertEqual(result, 1)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status_id, models.Statuses.APPROVED)

    def test_wrong_status_fails(self, patched_method):
        self.payment.status_id = models.Statuses.TRANSFERRED
        self.payment.save()
        result = services.approve_payments(payment_ids=[self.payment.id], username=self.user.username)
        self.assertEqual(result, 0)

    def test_other_approver_fails(self, patched_method):
        self.payment.approver = get_user_model().objects.create_user(username='other')
        self.payment.save()
        result = services.approve_payments(payment_ids=[self.payment.id], username=self.user.username)
        self.assertEqual(result, 0)
