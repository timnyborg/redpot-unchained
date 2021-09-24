from decimal import Decimal
from urllib.parse import urlencode

from django import test
from django.urls import reverse

from apps.core.utils.tests import LoggedInMixin, LoggedInViewTestMixin
from apps.enrolment.tests.factories import EnrolmentFactory
from apps.fee.tests.factories import FeeFactory

from .. import models, services


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
        self.assertEqual(self.enrolment.get_balance(), 100)


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
        self.assertEqual(self.enrolment.get_balance(), sum(fee.amount for fee in self.fees))


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
        self.assertEqual(self.enrolment.get_balance(), -100)


class TestMultipleEnrolmentSelectionView(LoggedInViewTestMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Setup an enrolment with fees owing. todo: consider a factory for this sort of case
        cls.enrolment = EnrolmentFactory()
        fee = FeeFactory(module=cls.enrolment.module)
        services.add_enrolment_fee(enrolment_id=cls.enrolment.id, fee_id=fee.id, user=cls.user)
        cls.url = reverse('finance:choose-multiple-enrolments', args=[cls.enrolment.qa.student.pk])

    def test_invalid_post(self):
        """Check that not selecting an enrolment returns an error"""
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You must select an enrolment')

    def test_post_redirects(self):
        """Check that we're forwarded to the correct location with enrolment id in the querystring"""
        response = self.client.post(self.url, data={'enrolment': self.enrolment.id})
        self.assertIn(reverse('finance:pay-multiple-enrolments'), response.url)
        self.assertIn(f'enrolment={self.enrolment.id}', response.url)


class TestMultipleEnrolmentPaymentView(LoggedInViewTestMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.enrolments: list = EnrolmentFactory.create_batch(size=2)
        query_string = urlencode({'enrolment': [enrolment.pk for enrolment in cls.enrolments]}, doseq=True)
        cls.url = reverse('finance:pay-multiple-enrolments') + f'?{query_string}'

    def test_post(self):
        """Check that we're forwarded to the correct location with enrolment id in the querystring"""
        response = self.client.post(
            self.url,
            data={
                'narrative': 'Test',
                'type': models.TransactionTypes.CREDIT_CARD,
                'amount': 20,
                f'allocation_{self.enrolments[0].pk}': 5,
                f'allocation_{self.enrolments[1].pk}': 15,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.enrolments[0].get_balance(), -5)


class TestReceiptPDF(LoggedInViewTestMixin, test.TestCase):
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        enrolment = EnrolmentFactory()
        transaction = services.insert_ledger(
            account_code=models.Accounts.CASH,
            amount=Decimal(100),
            user=cls.user,
            finance_code='TEST',
            narrative='TEST',
            enrolment_id=enrolment.id,
            type_id=models.TransactionTypes.CREDIT_CARD,
        )
        cls.url = reverse(
            'finance:receipt', kwargs={'allocation': transaction.account_line.allocation, 'enrolment_id': enrolment.id}
        )

    def test_get(self):
        """This can't actually verify the contents of the pdf"""
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/pdf')


class TestBatchViews(LoggedInMixin, test.TestCase):
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.transaction = services.insert_ledger(
            account_code=models.Accounts.CASH,
            amount=Decimal(100),
            user=cls.user,
            finance_code='test',
            narrative='test narrative',
            type_id=models.TransactionTypes.CREDIT_CARD,
        )

    def test_my_batches(self):
        """Check that the unbatched type is displayed"""
        response = self.client.get(reverse('finance:my-batches'))
        self.assertContains(response, 'Credit card')

    def test_all_batches_unbatched(self):
        """Check that the unbatched type is displayed"""
        response = self.client.get(reverse('finance:all-batches'), data={'unbatched': True})
        self.assertContains(response, 'Credit card')

    def test_all_batches_batched(self):
        response = self.client.get(reverse('finance:all-batches'), data={'unbatched': False})
        self.assertNotContains(response, 'Credit card')

    def test_create_batch(self):
        self.assertIsNone(self.transaction.account_line.batch)
        self.client.get(
            reverse(
                'finance:create-batch',
                kwargs={'type_id': models.TransactionTypes.CREDIT_CARD, 'created_by': self.user.username},
            )
        )
        self.transaction.account_line.refresh_from_db()
        self.assertIsNotNone(self.transaction.account_line.batch)

    def test_print_batch(self):
        models.Ledger.objects.filter(allocation=self.transaction.allocation).update(batch=1)
        response = self.client.get(reverse('finance:print-batch', kwargs={'batch': 1}))
        self.assertContains(response, 'test narrative')
