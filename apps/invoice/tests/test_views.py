from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.core.utils.tests import LoggedInMixin, LoggedInViewTestMixin
from apps.enrolment.tests.factories import EnrolmentFactory
from apps.finance.tests.factories import LedgerFactory
from apps.student.tests.factories import AddressFactory

from .. import models
from . import factories


class TestViewsWithLogin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        fee_line = LedgerFactory()
        cls.invoice = factories.InvoiceFactory()
        cls.invoice.ledger_items.add(
            fee_line,
            # Setting allocation is required so long as we use this awkward field (and have it as NOT NULL)
            through_defaults={'allocation': cls.invoice, 'item_no': 0},
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_search_loads(self):
        response = self.client.get(reverse('invoice:search'))
        self.assertEqual(response.status_code, 200)

    def test_search_with_outstanding_filter(self):
        # Todo: test for results with each of these
        response = self.client.get(reverse('invoice:search'), {'outstanding': 'on'})
        self.assertEqual(response.status_code, 200)

    def test_search_with_overdue_filter(self):
        response = self.client.get(reverse('invoice:search'), {'overdue': 'on'})
        self.assertEqual(response.status_code, 200)

    def test_search_without_filters(self):
        response = self.client.get(
            reverse('invoice:search'),
            {
                'invoiced_to': '',
                'minimum': '',
                'maximum': '',
                'created_by': '',
                'created_after': '',
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_view_invoice(self):
        response = self.client.get(reverse('invoice:view', args=[self.invoice.id]))
        # TODO: We should check for invoice data being present
        self.assertEqual(response.status_code, 200)

    def test_lookup_succeeds(self):
        response = self.client.post(reverse('invoice:lookup'), data={'number': f'XG{self.invoice.number}'})
        self.assertRedirects(response, self.invoice.get_absolute_url())
        response = self.client.post(reverse('invoice:lookup'), data={'number': self.invoice.number})
        self.assertRedirects(response, self.invoice.get_absolute_url())

    def test_lookup_fails(self):
        response = self.client.post(reverse('invoice:lookup'), data={'number': 'XG99999'})
        self.assertRedirects(response, '/invoice/search')

    def test_lookup_fails_with_bad_number(self):
        response = self.client.post(reverse('invoice:lookup'), data={'number': 'ABCDEFG'})
        self.assertRedirects(response, '/invoice/search')


class TestCreateViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.enrolment = EnrolmentFactory()
        cls.student = cls.enrolment.qa.student
        cls.address = AddressFactory(student=cls.student)  # Add an address to test default values
        cls.fees = LedgerFactory.create_batch(size=2, enrolment=cls.enrolment)

    def setUp(self):
        self.client.force_login(self.user)

    def test_choose_enrolments_get(self):
        response = self.client.get(reverse('invoice:choose-enrolments', args=[self.student.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['table'].rows), 1)

    def test_choose_fees_get(self):
        response = self.client.get(
            reverse('invoice:choose-fees', args=[self.student.pk]),
            data={'enrolment': self.enrolment.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['table'].rows), 2)

    def test_create_get_without_fees_raises_404(self):
        response = self.client.get(
            reverse('invoice:create', args=[self.student.pk]),
        )
        self.assertEqual(response.status_code, 404)

    def test_create_get(self):
        response = self.client.get(
            reverse('invoice:create', args=[self.student.pk]),
            data={'fee': [self.fees[0].pk]},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.address.line1)

    def test_create_post(self):
        response = self.client.post(
            reverse('invoice:create', args=[self.student.pk]) + f'?fee={self.fees[0].pk}&fee={self.fees[1].pk}',
            data={
                'due_date': date(2020, 1, 1),
                'invoiced_to': 'Person',
                'contact_person': 'Steve',
                'contact_email': 'a@a.net',
                'contact_phone': '123',
            },
        )
        self.assertEqual(response.status_code, 302)
        # Check the created invoice has the correct details
        invoice = models.Invoice.objects.last()
        self.assertEqual(invoice.invoiced_to, 'Person')
        self.assertEqual(invoice.amount, sum(f.amount for f in self.fees))
        self.assertEqual(invoice.ledger_items.count(), 2)


class TestRCPUpload(LoggedInViewTestMixin, TestCase):
    url = reverse('invoice:upload-rcp')

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user.is_superuser = True
        cls.user.save()

    def test_wrong_extension_error(self):
        file = SimpleUploadedFile('bad.txt', b'content')
        response = self.client.post(self.url, data={'file': file})
        self.assertIn('txt', response.context['form'].errors['file'][0])

    def test_invalid_encoding_error(self):
        file = SimpleUploadedFile('good.csv', 'content'.encode('utf-16'))
        response = self.client.post(self.url, data={'file': file})
        self.assertIn('Invalid', response.context['form'].errors['file'][0])

    def test_valid_upload(self):
        file = SimpleUploadedFile('good.csv', b'content')
        with patch('apps.invoice.services.add_repeating_payments_from_file') as mock_method:
            response = self.client.post(self.url, data={'file': file})
            self.assertEqual(response.status_code, 302)
            self.assertTrue(mock_method.called)


class TestCreatePaymentPlan(LoggedInViewTestMixin, TestCase):
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.invoice = factories.InvoiceFactory()
        cls.url = reverse('invoice:create-payment-plan', kwargs={'invoice_id': cls.invoice.pk})

    def test_create(self):
        response = self.client.post(
            self.url,
            data={
                'type': models.CUSTOM_PLAN_TYPE,
                'amount': 100,
                'status': models.CUSTOM_PAYMENT_PENDING_STATUS,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.invoice.payment_plan.amount, 100)


class TestPDFs(LoggedInMixin, TestCase):
    """Check that invoice pdfs render correctly.  These can't actually verify the contents of the pdf"""

    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.invoice = factories.InvoiceFactory()
        cls.invoice.ledger_items.add(
            LedgerFactory(),  # Todo: switch to a double-sided transaction
            through_defaults={'item_no': 1, 'allocation': cls.invoice},
        )

    def test_invoice(self):
        response = self.client.get(reverse('invoice:pdf', kwargs={'pk': self.invoice.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/pdf')

    def test_statement_without_schedule(self):
        response = self.client.get(reverse('invoice:statement', kwargs={'pk': self.invoice.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/pdf')

    def test_statement_with_schedule(self):
        payment_plan = factories.CustomPaymentPlanFactory(invoice=self.invoice)
        factories.ScheduledPaymentFactory.create_batch(size=2, payment_plan=payment_plan)
        response = self.client.get(reverse('invoice:statement', kwargs={'pk': self.invoice.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/pdf')
