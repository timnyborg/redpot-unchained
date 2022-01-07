import io
from datetime import datetime
from decimal import Decimal

from django import test

import apps.finance.services as finance_services
from apps.core.models import User
from apps.core.tests.factories import UserFactory
from apps.enrolment.tests.factories import EnrolmentFactory
from apps.fee.tests.factories import FeeFactory
from apps.finance.models import Accounts, TransactionTypes
from apps.finance.tests.factories import LedgerFactory

from .. import services
from . import factories


class TestAddPayment(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        """Prep an invoice with two enrolments with £50 and £100 outstanding
        Todo: figure out a concise way to do this
        """
        cls.user = User(username='testuser')
        cls.invoice = factories.InvoiceFactory()
        fees = [FeeFactory(amount=50), FeeFactory(amount=100)]
        cls.enrolments = [EnrolmentFactory(module=fee.module) for fee in fees]
        for fee, enrolment in zip(fees, cls.enrolments):
            transaction = finance_services.add_enrolment_fee(enrolment_id=enrolment.id, fee_id=fee.id, user=cls.user)
            services.attach_transaction_to_invoice(transaction=transaction, invoice=cls.invoice)

    def test_fails_when_lacking_enrolments(self):
        invoice = factories.InvoiceFactory()
        with self.assertRaises(services.NoValidEnrolmentsError):
            services.add_payment(
                invoice=invoice,
                amount=Decimal(100),
                type_id=TransactionTypes.CREDIT_CARD,
                user=self.user,
                narrative='Test',
            )

    def test_single_enrolment_payment(self):
        """Check that a payment is only applied to a specified enrolment"""
        services.add_payment(
            invoice=self.invoice,
            amount=Decimal(10),
            type_id=TransactionTypes.CREDIT_CARD,
            user=self.user,
            narrative='Test payment',
            enrolment=self.enrolments[0],
        )
        self.assertEqual(self.enrolments[0].get_balance(), 40)

    def test_multiple_enrolment_payment(self):
        """Check that a partial payment is distributed among the enrolments, weighted by value"""
        services.add_payment(
            invoice=self.invoice,
            amount=Decimal(120),
            type_id=TransactionTypes.CREDIT_CARD,
            user=self.user,
            narrative='Test payment',
        )
        self.assertEqual(self.enrolments[0].get_balance(), 10)
        self.assertEqual(self.enrolments[1].get_balance(), 20)


class TestAddCredit(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        """Prep an invoice"""
        cls.user = User(username='testuser')
        cls.invoice = factories.InvoiceFactory()
        fee = FeeFactory(amount=100)
        cls.enrolment = EnrolmentFactory(module=fee.module)
        transaction = finance_services.add_enrolment_fee(enrolment_id=cls.enrolment.id, fee_id=fee.id, user=cls.user)
        services.attach_transaction_to_invoice(transaction=transaction, invoice=cls.invoice)

    def test_add_credit(self):
        """Check credit is added to the enrolment"""
        services.add_credit(
            invoice=self.invoice,
            amount=Decimal(50),
            type_id=TransactionTypes.CREDIT_CARD,
            user=self.user,
            narrative='Test credit',
            enrolment=self.enrolment,
            account_code=Accounts.TUITION,
        )
        self.assertEqual(self.enrolment.get_balance(), 50)


class TestRCP(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        UserFactory(username='service_user')  # todo: remove once service user added by migrations
        ledger_item = LedgerFactory(amount=100)
        cls.invoice = factories.InvoiceFactory(number=10)
        cls.invoice.ledger_items.add(ledger_item, through_defaults={'allocation': cls.invoice, 'item_no': 1})

    def test_valid_payment(self):
        file = io.BytesIO(b'10,,,Name,1234,mc,50.00,ref code,01/02/20 00:00,success')

        services.add_repeating_payments_from_file(file=file)

        self.assertEqual(self.invoice.get_payments().count(), 1)
        payment = self.invoice.get_payments().first()
        self.assertEqual(payment.timestamp, datetime(2020, 2, 1))
        self.assertIn('ref code', payment.narrative)

    def test_invalid_amount(self):
        file = io.BytesIO(b'10,,,Name,1234,mc,-50.00,ref code,01/02/20 00:00,success')
        services.add_repeating_payments_from_file(file=file)
        self.assertEqual(self.invoice.get_payments().count(), 0)

    def test_invalid_status(self):
        file = io.BytesIO(b'10,,,Name,1234,mc,-50.00,ref code,01/02/20 00:00,failure')
        services.add_repeating_payments_from_file(file=file)
        self.assertEqual(self.invoice.get_payments().count(), 0)
