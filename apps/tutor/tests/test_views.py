from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.template import TemplateDoesNotExist

DOCX_MIMETYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class TestViewsWithLogin(TestCase):
    fixtures = ['test_tutor_module.yaml']

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')

    def setUp(self):
        self.client.force_login(self.user)

    def test_tutor_module_view(self):
        response = self.client.get(reverse('tutor:module:view', args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_expense_form_single(self):
        response = self.client.get(reverse('tutor:expense-form-single', args=[1, 'weekly']))
        # Check that it returns a docx file
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), DOCX_MIMETYPE)
        self.assertIn(".docx", response.get('Content-Disposition'))

    def test_expense_form_module(self):
        response = self.client.get(reverse('tutor:expense-form-module', args=[1, 'weekly']))
        # Check that it returns a docx file
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), DOCX_MIMETYPE)
        self.assertIn(".docx", response.get('Content-Disposition'))

    def test_expense_form_missing_template(self):
        # Check that it returns a docx file
        with self.assertRaises(TemplateDoesNotExist):
            self.client.get(reverse('tutor:expense-form-single', args=[1, 'bad-name']))
