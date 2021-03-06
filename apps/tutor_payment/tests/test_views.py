from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django import test
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models import Sum
from django.urls import reverse

from apps.core.utils.tests import LoggedInMixin, LoggedInViewTestMixin
from apps.tutor.tests.factories import TutorModuleFactory

from .. import models, views
from . import factories


class TestCreatePayment(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        permissions = [
            Permission.objects.get(content_type__app_label='tutor_payment', codename='raise'),
            Permission.objects.get(content_type__app_label='tutor_payment', codename='approve'),
        ]
        cls.user.user_permissions.add(*permissions)
        cls.tutor_on_module = TutorModuleFactory()
        cls.url = reverse('tutor-payment:new', args=[cls.tutor_on_module.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        response = self.client.post(
            self.url,
            data={
                'hourly_rate': 5,
                'hours_worked': 5,
                'amount': 25,
                'weeks': 4,
                'type': models.Types.ADMIN,
                'approver': 'testuser',
            },
        )
        self.assertEqual(response.status_code, 302)


class TestEditPayment(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        permissions = [
            Permission.objects.get(content_type__app_label='tutor_payment', codename='raise'),
            Permission.objects.get(content_type__app_label='tutor_payment', codename='approve'),
        ]
        cls.user.user_permissions.add(*permissions)
        cls.payment = factories.PaymentFactory(raised_by=cls.user, approver=cls.user, amount=50)
        cls.url = reverse('tutor-payment:edit', args=[cls.payment.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post(
            self.url,
            data={
                'hourly_rate': 5,
                'hours_worked': 5,
                'amount': 25,
                'weeks': 4,
                'type': models.Types.ADMIN,
                'approver': 'testuser',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.amount, 25)


class TestExtras(LoggedInMixin, test.TestCase):
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user.user_permissions.add(
            Permission.objects.get(content_type__app_label='tutor_payment', codename='approve')
        )
        cls.tutor_module = TutorModuleFactory(module__start_date=date(2020, 1, 1), module__end_date=date(2021, 1, 1))
        cls.url = reverse('tutor-payment:quick:extras', kwargs={'pk': cls.tutor_module.pk})

        models.PaymentRate.objects.create(tag='online_extra_student', amount=20)
        models.PaymentRate.objects.create(tag='marking_rate', amount=6)
        cls.summative_rate = models.PaymentRate.objects.create(type='summative', amount=10, description='Summ')
        cls.formative_rate = models.PaymentRate.objects.create(type='formative', amount=10, description='Form')

    def test_create_formative(self):
        response = self.client.post(
            self.url,
            data={
                'formative': 5,
                'formative_rate': self.formative_rate.pk,
                'approver': 'testuser',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.TutorPayment.objects.last().approver, self.user)

    def test_create_summative(self):
        response = self.client.post(
            self.url,
            data={
                'summative': 5,
                'summative_rate': self.summative_rate.pk,
                'approver': 'testuser',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.TutorPayment.objects.last().approver, self.user)

    def test_extra_students(self):
        response = self.client.post(
            self.url,
            data={
                'extra_students': 5,
                'approver': 'testuser',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.TutorPayment.objects.last().approver, self.user)


class TestSyllabus(LoggedInMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user.default_approver = cls.user
        cls.user.save()
        cls.tutor_module = TutorModuleFactory(module__start_date=date(2000, 1, 1))
        models.PaymentRate.objects.create(tag='weekly_hourly_rate', amount=10)
        cls.url = reverse('tutor-payment:quick:syllabus', kwargs={'pk': cls.tutor_module.pk})

    def test_fails_without_approver(self):
        self.user.default_approver = None
        self.user.save()
        self.client.post(self.url)
        self.assertEqual(self.tutor_module.payments.count(), 0)

    def test_fails_without_start_date(self):
        self.tutor_module.module.start_date = None
        self.tutor_module.module.save()
        self.client.post(self.url)
        self.assertEqual(self.tutor_module.payments.count(), 0)

    def test_create(self):
        self.client.post(self.url)
        self.assertEqual(self.tutor_module.payments.count(), 2)  # 1 payment + 1 holiday
        self.assertEqual(self.tutor_module.payments.aggregate(sum=Sum('amount'))['sum'], 30)


class TestApprove(LoggedInViewTestMixin, test.TestCase):
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.payment = factories.PaymentFactory(status_id=models.Statuses.RAISED, raised_by=cls.user, approver=cls.user)
        cls.url = reverse('tutor-payment:approve')

    @patch('apps.tutor_payment.models.TutorPayment.approvable', return_value=True)
    def test_post(self, patched_method):
        response = self.client.post(self.url, {'payment': [self.payment.id]})
        self.assertEqual(response.status_code, 302)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status_id, models.Statuses.APPROVED)


class TestTeachingPaymentViews(LoggedInMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        permissions = [
            Permission.objects.get(content_type__app_label='tutor_payment', codename='raise'),
            Permission.objects.get(content_type__app_label='tutor_payment', codename='approve'),
        ]
        models.PaymentRate.objects.create(tag='online_hourly_rate', amount=Decimal(20))
        models.PaymentRate.objects.create(tag='weekly_hourly_rate', amount=Decimal(20))
        cls.online_payment_rate = models.PaymentRate.objects.create(type='online_teaching', amount=Decimal(500))
        cls.tutor_module = TutorModuleFactory(module__start_date=date(2020, 1, 1))
        cls.user.user_permissions.add(*permissions)

    def test_get_weekly(self):
        response = self.client.get(reverse('tutor-payment:quick:weekly-teaching', args=[self.tutor_module.id]))
        self.assertEqual(response.status_code, 200)

    @patch('apps.tutor_payment.services.create_teaching_fee')
    def test_post_weekly(self, create_teaching_fee: MagicMock):
        """Check that posting succeeds and calls the service with the correct total"""
        response = self.client.post(
            reverse('tutor-payment:quick:weekly-teaching', args=[self.tutor_module.id]),
            data={'schedule': 1, 'length': Decimal(2), 'no_meetings': 10, 'approver': self.user.username},
        )
        self.assertEqual(response.status_code, 302)
        create_teaching_fee.assert_called_once()
        self.assertEqual(create_teaching_fee.call_args[1]['amount'], Decimal(2 * 10 * 20))

    def test_get_online(self):
        response = self.client.get(reverse('tutor-payment:quick:online-teaching', args=[self.tutor_module.id]))
        self.assertEqual(response.status_code, 200)

    @patch('apps.tutor_payment.services.create_teaching_fee')
    def test_post_online(self, create_teaching_fee: MagicMock):
        """Check that posting succeeds and calls the service"""
        response = self.client.post(
            reverse('tutor-payment:quick:online-teaching', args=[self.tutor_module.id]),
            data={'schedule': 1, 'amount': self.online_payment_rate.id, 'approver': self.user.username},
        )
        self.assertEqual(response.status_code, 302)
        create_teaching_fee.assert_called_once()


class TestExportCSV(LoggedInMixin, test.TestCase):
    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.payment = factories.PaymentFactory(
            tutor_module__tutor__student__surname='Smith',
            batch=1,
            type_id=models.Types.TEACHING,
            status_id=models.Statuses.TRANSFERRED,
            raised_by=cls.user,
            amount=Decimal(100),
            weeks=4,
        )

    def test_permanent_staff_payments_undivided(self):
        # permanent staff
        self.payment.tutor_module.tutor.appointment_id = 'perm'
        self.payment.tutor_module.tutor.save()

        result = views.Export.get_csv_rows(batch=1)

        self.assertEqual(result[0]['cash_value'], Decimal('100'))
        self.assertEqual(len(result), 1)

    def test_casual_staff_payments_divided_by_week(self):
        # casual staff
        self.payment.tutor_module.tutor.appointment_id = 'castch1'
        self.payment.tutor_module.tutor.save()

        result = views.Export.get_csv_rows(batch=1)

        self.assertEqual(result[0]['cash_value'], Decimal('25'))
        self.assertEqual(len(result), 4)

    def test_response_data(self):
        response = self.client.get(reverse('tutor-payment:export'), data={'batch': 1})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smith')
