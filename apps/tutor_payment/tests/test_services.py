from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django import test
from django.contrib.auth import get_user_model

from apps.core.tests.factories import UserFactory
from apps.tutor.tests.factories import TutorModuleFactory

from .. import models, services
from . import factories


@patch('apps.tutor_payment.models.TutorPayment.approvable', return_value=True)  # We only want to test approvable items
class TestApprovePayments(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        # begin with an approvable payment
        cls.payment = factories.PaymentFactory(status_id=models.Statuses.RAISED, raised_by=cls.user, approver=cls.user)

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


class TestCreateTeachingFee(test.TestCase):
    def test_create(self):
        user = UserFactory()
        tutor_module = TutorModuleFactory(module__start_date=date(2020, 1, 1))
        services.create_teaching_fee(
            tutor_module=tutor_module,
            amount=Decimal(100),
            rate=Decimal(20),
            schedule=models.Schedule(months=3, first_month=3, label='Test Schedule'),
            raised_by=user,
            approver=user,
        )
        payments = list(tutor_module.payments.all())
        self.assertEqual(len(payments), 4)  # 1 per month + 1 holiday pay
        self.assertEqual(sum(payment.amount for payment in payments), Decimal(100))
        self.assertEqual(
            {payment.pay_after for payment in payments},
            {date(2020, 3, 1), date(2020, 4, 1), date(2020, 5, 1)},  # Correct month generation from the schedule
        )
