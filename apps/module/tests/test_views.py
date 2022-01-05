from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.core.utils.tests import LoggedInMixin, LoggedInViewTestMixin
from apps.enrolment.tests.factories import EnrolmentFactory
from apps.fee.models import FeeTypes
from apps.fee.tests.factories import FeeFactory
from apps.hesa.models import HECoSSubject
from apps.invoice.models import PaymentPlanType
from apps.programme.models import ProgrammeModule
from apps.programme.tests.factories import ProgrammeFactory
from apps.tutor.tests.factories import TutorModuleFactory

from ..models import Module, ModuleStatus
from . import factories


class TestViewsWithoutLogin(TestCase):
    def test_views_require_login(self):
        response = self.client.get(reverse('module:search'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('module:edit', args=[1]))
        self.assertEqual(response.status_code, 302)
        response = self.client.patch(reverse('module:update-api', args=[1]))
        self.assertEqual(response.status_code, 403)


class TestViewsWithLogin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.object = factories.ModuleFactory()

    def setUp(self):
        self.client.force_login(self.user)

    def test_search_loads(self):
        response = self.client.get(reverse('module:search'))
        self.assertEqual(response.status_code, 200)

    def test_search_limited_years(self):
        # todo: parameterized search testing using subtests or parameterized
        response = self.client.get(reverse('module:search'), data={'limit_years': 'on'})
        table = response.context['table']
        self.assertEqual(len(table.rows), 0)

    def test_search_unlimited_years(self):
        response = self.client.get(reverse('module:search'), data={'limit_years': ''})
        table = response.context['table']
        self.assertEqual(len(table.rows), 1)

    def test_view_page(self):
        response = self.client.get(reverse('module:view', args=[self.object.pk]))
        self.assertEqual(response.status_code, 200)

    def test_edit_page(self):
        response = self.client.get(reverse('module:edit', args=[self.object.pk]))
        self.assertEqual(response.status_code, 200)

    def test_toggle_autoreminder(self):
        # todo: move all api tests to a new file
        """Test that auto_reminder is toggled from True -> False, then False -> True"""
        response = self.client.patch(
            reverse('module:update-api', args=[self.object.pk]),
            data={'auto_reminder': False},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.object.refresh_from_db()
        self.assertEqual(self.object.auto_reminder, False)

        response = self.client.patch(
            reverse('module:update-api', args=[self.object.pk]),
            data={'auto_reminder': True},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.object.refresh_from_db()
        self.assertEqual(self.object.auto_reminder, True)

    def test_toggle_autofeedback(self):
        """Test that auto_feedback is toggled from True -> False, then False -> True"""
        response = self.client.patch(
            reverse('module:update-api', args=[self.object.pk]),
            data={'auto_feedback': False},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.object.refresh_from_db()
        self.assertEqual(self.object.auto_feedback, False)

        response = self.client.patch(
            reverse('module:update-api', args=[self.object.pk]),
            data={'auto_feedback': True},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.object.refresh_from_db()
        self.assertEqual(self.object.auto_feedback, True)

    def test_new_page_get(self):
        response = self.client.get(reverse('module:new'))
        self.assertEqual(response.status_code, 200)

    def test_new_page_post(self):
        response = self.client.post(
            reverse('module:new'),
            data={'code': 'T12T123TTT', 'title': 'Test', 'division': 1, 'portfolio': 1, 'non_credit_bearing': True},
        )
        # Check that we've been forwarded, and the new module was created
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Module.objects.last().code, 'T12T123TTT')


class TestCloneView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.object = factories.ModuleFactory()
        cls.url = reverse('module:clone', args=[cls.object.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_clone(self):
        response = self.client.post(
            self.url,
            data={
                'title': 'New title',
                'code': 'T99T123TTT',
                'keep_url': True,
                'copy_fees': True,
                'copy_dates': False,
            },
        )
        self.assertEqual(response.status_code, 302)
        new_module = Module.objects.last()

        self.assertEqual(new_module.url, self.object.url)
        self.assertEqual(new_module.title, 'New title')
        self.assertIsNone(new_module.start_date)


class TestAddProgrammeView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.module = factories.ModuleFactory()
        cls.programme = ProgrammeFactory()
        cls.url = reverse('module:add-programme', args=[cls.module.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_add_programme(self):
        response = self.client.post(
            self.url,
            data={
                'module': self.module.pk,
                'programme': self.programme.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ProgrammeModule.objects.last().module_id, self.module.pk)


class TestExcelExportViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.module = factories.ModuleFactory()
        cls.enrolment = EnrolmentFactory(module=cls.module)

    def setUp(self):
        self.client.force_login(self.user)

    def test_student_list(self):
        url = reverse('module:student-list', args=[self.module.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheetml', response['content-type'])

    def test_moodle_list(self):
        url = reverse('module:moodle-list', args=[self.module.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheetml', response['content-type'])


class TestAssignMoodleIDsView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.enrolment = EnrolmentFactory()
        cls.url = reverse('module:assign-moodle-ids', args=[cls.enrolment.module.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_student_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        # Check that a moodle record has been created with the right details
        moodle_record = self.enrolment.qa.student.moodle_id
        self.assertEqual(moodle_record.first_module_code, self.enrolment.module.code)
        self.assertEqual(moodle_record.created_by, self.user.username)


class TestCopyFees(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.source_module = factories.ModuleFactory()
        cls.target_module = factories.ModuleFactory()
        cls.source_fee = FeeFactory(module=cls.source_module)
        cls.url = reverse('module:copy-fees', args=[cls.target_module.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_copy(self):
        response = self.client.post(self.url, data={'source_module': self.source_module.id})
        self.assertEqual(response.status_code, 302)
        new_fee = self.target_module.fees.last()
        self.assertEqual(new_fee.amount, self.source_fee.amount)
        self.assertEqual(new_fee.description, self.source_fee.description)


class TestCopyWebFields(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.source_module = factories.ModuleFactory(overview='Details!')
        cls.target_module = factories.ModuleFactory()
        cls.url = reverse('module:copy-web-fields', args=[cls.target_module.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_copy(self):
        response = self.client.post(self.url, data={'source_module': self.source_module.id})
        self.assertEqual(response.status_code, 302)
        self.target_module.refresh_from_db(fields=['overview'])  # `fields` works around defer()
        self.assertEqual(self.target_module.overview, 'Details!')


class TestHESASubjectEditView(LoggedInViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # todo: replace with subject fixtures
        HECoSSubject.objects.create(id=100003, name='Ceramics')
        HECoSSubject.objects.create(id=100005, name='Clinical engineering')
        cls.module = factories.ModuleFactory(non_credit_bearing=False)
        cls.url = reverse('module:edit-hesa-subjects', kwargs={'pk': cls.module.pk})

    def test_post(self):
        response = self.client.post(
            self.url,
            data={
                'module_hecos_subjects-TOTAL_FORMS': 2,
                'module_hecos_subjects-INITIAL_FORMS': 0,
                'module_hecos_subjects-0-hecos_subject': 100003,
                'module_hecos_subjects-0-percentage': 25,
                'module_hecos_subjects-1-hecos_subject': 100005,
                'module_hecos_subjects-1-percentage': 75,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.module.hecos_subjects.count(), 2)


class TestCancelAndUncancelView(LoggedInViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.module = factories.ModuleFactory(status=ModuleStatus.objects.get(id=22))
        cls.cancel_module_url = reverse('module:cancel', args=[cls.module.pk])
        cls.cancelled_module = factories.ModuleFactory(
            status=ModuleStatus.objects.get(id=33), is_cancelled=True, auto_feedback=False, auto_reminder=False
        )
        cls.uncancel_module_url = reverse('module:uncancel', args=[cls.cancelled_module.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_cancel_module(self):
        self.assertNotEqual(self.module.status.id, 33)
        response = self.client.post(self.cancel_module_url)
        self.assertEqual(response.status_code, 302)
        self.module.refresh_from_db()
        self.assertTrue(self.module.is_cancelled)
        self.assertFalse(self.module.auto_feedback)
        self.assertFalse(self.module.auto_reminder)
        self.assertEqual(self.module.status.id, 33)

    def test_uncancel_module(self):
        self.assertEqual(self.cancelled_module.status.id, 33)
        response = self.client.post(self.uncancel_module_url, data={'status': 20})
        self.cancelled_module.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.cancelled_module.status.id, 20)
        self.assertFalse(self.cancelled_module.auto_feedback)
        self.assertFalse(self.cancelled_module.auto_reminder)
        self.assertFalse(self.cancelled_module.is_cancelled)


class TestPaymentPlanViews(LoggedInMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.module = factories.ModuleFactory()
        cls.plan_type = PaymentPlanType.objects.create(name='Plan', deposit=Decimal(0))

    def test_add_plan(self):
        response = self.client.post(
            reverse('module:add-payment-plan', args=[self.module.id]), data={'plan_type': self.plan_type.id}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.module.payment_plans.count(), 1)

    def test_remove_plan(self):
        self.module.payment_plans.add(self.plan_type)
        response = self.client.post(reverse('module:remove-payment-plan', args=[self.module.id, self.plan_type.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.module.payment_plans.count(), 0)


class TestClassRegister(LoggedInViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.enrolment = EnrolmentFactory(module__portfolio_id=32)

    def test_get(self):
        """Check the view renders at all - we can't inspect the docx file's contents"""
        response = self.client.get(path=reverse('module:class-register', args=[self.enrolment.module.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('word', response['content-type'])


class TestSyllabus(LoggedInViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.module = factories.ModuleFactory()
        FeeFactory(module=cls.module, type_id=FeeTypes.PROGRAMME, amount=500)
        cls.tutor_module = TutorModuleFactory(module=cls.module, is_teaching=True)

    def test_get(self):
        response = self.client.get(path=reverse('module:syllabus', args=[self.module.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '£500')
        self.assertContains(response, self.module.title)
        self.assertContains(response, str(self.tutor_module.tutor.student))
