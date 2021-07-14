from decimal import Decimal

from django import test
from django.contrib.auth import get_user_model

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
