from datetime import date

from freezegun import freeze_time

from django import test
from django.core import mail
from django.urls import reverse

from apps.core.utils.tests import LoggedInMixin, LoggedInViewTestMixin
from apps.fee.tests.factories import FeeFactory
from apps.finance import services as finance_services
from apps.finance.services import add_enrolment_fee
from apps.invoice import services as invoice_services
from apps.invoice.tests.factories import InvoiceFactory
from apps.module.tests.factories import ModuleFactory
from apps.qualification_aim.tests.factories import QualificationAimFactory

from .. import models
from . import factories


class TestDetailView(LoggedInViewTestMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Setup an enrolment with one fee added
        cls.enrolment = factories.EnrolmentFactory()
        cls.fee = FeeFactory(module=cls.enrolment.module)
        add_enrolment_fee(
            enrolment_id=cls.enrolment.id,
            fee_id=cls.fee.id,
            user=cls.user,
        )
        cls.url = cls.enrolment.get_absolute_url()

    def test_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.fee.description)


@freeze_time('2020-01-01')
class TestCreateView(LoggedInViewTestMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.qa = QualificationAimFactory(student__gender=None)
        cls.url = reverse('enrolment:create', kwargs={'qa_id': cls.qa.pk})
        cls.module = ModuleFactory(start_date=date(2021, 1, 1))
        cls.module.programmes.add(cls.qa.programme)

    def test_create_updates_student(self):
        response = self.client.post(
            self.get_url(),
            data={
                'module': self.module.pk,
                'status': models.Statuses.CONFIRMED,
                'gender': 'F',
                'nationality': 270,
                # unchanged values
                'domicile': self.qa.student.domicile_id,
                'religion_or_belief': self.qa.student.religion_or_belief_id,
                'ethnicity': self.qa.student.ethnicity_id,
            },
        )
        self.qa.student.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.qa.student.gender, 'F')
        self.assertEqual(self.qa.student.nationality_id, 270)


class TestEditView(LoggedInViewTestMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.enrolment = factories.EnrolmentFactory()
        cls.url = reverse('enrolment:edit', kwargs={'pk': cls.enrolment.pk})

    def test_post(self):
        response = self.client.post(
            self.url,
            data={
                'status': models.Statuses.PROVISIONAL,
                'result': models.Results.PASSED,
                'module': self.enrolment.module_id,
                'qa': self.enrolment.qa_id,
            },
        )
        self.assertRedirects(response, self.enrolment.get_absolute_url())


class TestDeleteView(LoggedInViewTestMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.enrolment = factories.EnrolmentFactory()
        cls.url = reverse('enrolment:delete', kwargs={'pk': cls.enrolment.pk})

    def test_delete(self):
        self.client.post(self.url)
        with self.assertRaises(models.Enrolment.DoesNotExist):
            self.enrolment.refresh_from_db()


class TestConfirmationEmail(LoggedInMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Connect an invoice to an enrolment.  todo: a more complex factory for these use cases
        cls.invoice = InvoiceFactory()
        fee = FeeFactory(amount=100)
        cls.enrolment = factories.EnrolmentFactory(module=fee.module)
        transaction = finance_services.add_enrolment_fee(enrolment_id=cls.enrolment.id, fee_id=fee.id, user=cls.user)
        invoice_services.attach_transaction_to_invoice(transaction=transaction, invoice=cls.invoice)

    def test_get_by_enrolment(self):
        response = self.client.get(reverse('enrolment:confirmation-email', kwargs={'enrolment': self.enrolment.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        self.assertEqual(message.to, [self.user.email])
        self.assertEqual(len(message.attachments), 1)

    def test_get_by_invoice(self):
        response = self.client.get(
            reverse('enrolment:confirmation-email-by-invoice', kwargs={'invoice': self.invoice.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        self.assertEqual(message.to, [self.user.email])
        self.assertEqual(len(message.attachments), 1)

    def test_fails_if_lacking_email(self):
        self.user.email = ''
        self.user.save()
        self.client.get(reverse('enrolment:confirmation-email', kwargs={'enrolment': self.enrolment.pk}))
        self.assertEqual(len(mail.outbox), 0)
