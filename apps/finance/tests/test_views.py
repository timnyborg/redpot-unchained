from django import test
from django.urls import reverse

from apps.core.utils.tests import LoggedInMixin, LoggedInViewTestMixin
from apps.enrolment.tests.factories import EnrolmentFactory
from apps.fee.tests.factories import FeeFactory

from .. import models


class TestAddFeesView(LoggedInViewTestMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.enrolment = EnrolmentFactory()
        cls.fee = FeeFactory(module=cls.enrolment.module)
        cls.url = reverse('finance:add-fees', args=[cls.enrolment.pk])

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        # Check that the datatable includes the module fee
        self.assertContains(response, self.fee.description)

    def test_create_bespoke_fee(self):
        response = self.client.post(
            self.get_url(),
            data={
                'amount': 100,
                'narrative': 'Test fee',
                'account': models.Accounts.TUITION,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.enrolment.balance(), 100)


class TestAddModuleFeesView(LoggedInMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.enrolment = EnrolmentFactory()
        cls.fees = FeeFactory.create_batch(module=cls.enrolment.module, size=2)
        cls.url = reverse('finance:add-module-fees', args=[cls.enrolment.pk])

    def test_create_fees(self):
        response = self.client.post(self.url, data={'fee': [fee.id for fee in self.fees]})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.enrolment.ledger_set.debts().count(), 2)
        self.assertEqual(self.enrolment.balance(), sum(fee.amount for fee in self.fees))


class TestAddPaymentView(LoggedInViewTestMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.enrolment = EnrolmentFactory()
        cls.url = reverse('finance:add-payment', args=[cls.enrolment.pk])

    def test_create_payment(self):
        response = self.client.post(
            self.get_url(),
            data={'amount': 100, 'narrative': 'Test payment', 'type': models.TransactionTypes.CREDIT_CARD},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.enrolment.balance(), -100)
