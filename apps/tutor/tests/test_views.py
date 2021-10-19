from datetime import date

from django.contrib.auth import get_user_model
from django.template import TemplateDoesNotExist
from django.test import TestCase
from django.urls import reverse

from apps.core.utils.tests import LoggedInViewTestMixin
from apps.student.tests.factories import AddressFactory

from .. import models
from . import factories

DOCX_MIMETYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class TestViewsWithLogin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.tutor_module = factories.TutorModuleFactory()
        AddressFactory(student=cls.tutor_module.tutor.student)

    def setUp(self):
        self.client.force_login(self.user)

    def test_tutor_module_view(self):
        response = self.client.get(reverse('tutor:module:view', args=[self.tutor_module.id]))
        self.assertEqual(response.status_code, 200)

    def test_expense_form_single(self):
        response = self.client.get(reverse('tutor:expense-form-single', args=[self.tutor_module.id, 'weekly']))
        # Check that it returns a docx file
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), DOCX_MIMETYPE)
        self.assertIn(".docx", response.get('Content-Disposition'))

    def test_expense_form_module(self):
        response = self.client.get(reverse('tutor:expense-form-module', args=[self.tutor_module.module_id, 'weekly']))
        # Check that it returns a docx file
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), DOCX_MIMETYPE)
        self.assertIn(".docx", response.get('Content-Disposition'))

    def test_expense_form_missing_template(self):
        # Check that it returns a docx file
        with self.assertRaises(TemplateDoesNotExist):
            self.client.get(reverse('tutor:expense-form-single', args=[self.tutor_module.id, 'bad-name']))


class TestCreateTutorOnModule(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.tutor = factories.TutorFactory()
        cls.module = factories.ModuleFactory()
        cls.url = reverse('tutor:module:new')

    def setUp(self):
        self.client.force_login(self.user)

    def test_bad_ids_return_404(self):
        """Should require either tutor or module to be provided"""
        response = self.client.get(self.url, data={'module': 0})
        self.assertEqual(response.status_code, 404)
        response = self.client.get(self.url, data={'tutor': 0})
        self.assertEqual(response.status_code, 404)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_fields_prefilled(self):
        """When a tutor or module is provided, it should be displayed"""
        response = self.client.get(self.url, data={'module': self.module.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.module.title)
        response = self.client.get(self.url, data={'tutor': self.tutor.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tutor.student.firstname)

    def test_post(self):
        """Check that form submission works as expected"""
        response = self.client.post(
            f'{self.url}?tutor={self.tutor.pk}',
            data={
                'tutor': self.tutor.pk,
                'module': self.module.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            models.TutorModule.objects.last().tutor_id,
            self.tutor.id,
        )


class TestCreateActivity(LoggedInViewTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.tutor = factories.TutorFactory()
        cls.activity = models.ActivityType.objects.create(description='Test activity')
        cls.url = reverse('tutor:activity:new', args=[cls.tutor.pk])

    def test_post(self):
        response = self.client.post(
            self.url,
            data={'activity': self.activity.pk, 'date': date(2020, 1, 1)},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.TutorActivity.objects.last().tutor_id, self.tutor.pk)
