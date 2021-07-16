from decimal import Decimal

from django import test
from django.contrib.auth import get_user_model

from apps.enrolment.tests.factories import EnrolmentFactory
from apps.fee.tests.factories import FeeFactory

from .. import models, services


class TestInsertLedger(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')

    def test_dual_insert(self):
        services.insert_ledger(
            account_id=models.Accounts.TUITION,
            amount=Decimal(500),
            user=self.user,
            finance_code='ABCDE',
            narrative='Test transaction',
            type_id=1,  # Fee # todo: enum
        )
        self.assertEqual(models.Ledger.objects.count(), 2)
        self.assertEqual(models.Ledger.objects.total(), 0)


class TestAddEnrolmentFee(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.enrolment = EnrolmentFactory()

    def test_adding_catering_and_accommodation(self):
        fee = FeeFactory(is_catering=True, is_single_accom=True)
        services.add_enrolment_fee(
            enrolment_id=self.enrolment.id,
            fee_id=fee.id,
            user=self.user,
        )
        self.assertEqual(self.enrolment.accommodation.count(), 1)
        self.assertEqual(self.enrolment.catering.count(), 1)

    def test_max_discount(self):
        fee = FeeFactory()
        with self.assertRaises(ValueError):
            services.add_enrolment_fee(
                discount=100,
                enrolment_id=self.enrolment.id,
                fee_id=fee.id,
                user=self.user,
            )
