from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.programme.tests.factories import ProgrammeFactory
from apps.student.tests.factories import StudentFactory

from .. import models
from . import factories


class TestDetailsView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.object = factories.QualificationAimFactory()
        cls.url = reverse('qualification_aim:view', args=[cls.object.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class TestCreateView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.student = StudentFactory()
        cls.programme = ProgrammeFactory()

        cls.url = reverse('qualification_aim:new', args=[cls.student.pk])

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        response = self.client.post(
            self.url,
            data={
                'student': self.student.pk,
                'programme': self.programme.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        qa = models.QualificationAim.objects.last()
        self.assertEqual(qa.student_id, self.student.pk)


class TestEditView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.qa = factories.QualificationAimFactory()
        cls.url = cls.qa.get_edit_url()

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        response = self.client.post(
            self.url,
            data={
                'title': 'Test title',
                'study_location': models.AT_PROVIDER_STUDY_LOCATION,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.qa.refresh_from_db()
        self.assertEqual(self.qa.title, 'Test title')


class TestDeleteView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.qa = factories.QualificationAimFactory()
        cls.url = cls.qa.get_delete_url()

    def setUp(self):
        self.client.force_login(self.user)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        response = self.client.post(
            self.url,
            data={},
        )
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(models.QualificationAim.DoesNotExist):
            self.qa.refresh_from_db()
