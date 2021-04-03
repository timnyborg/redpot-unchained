from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.module.models import Module
from apps.student.models import Student
from apps.tutor.models import Tutor, TutorModule

from ..models import TutorFee, TutorFeeRate


class TestExtras(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='testuser')
        cls.module = Module.objects.create(
            title='Test module',
            start_date=date(2000, 1, 1),
            end_date=date(2001, 1, 1),
        )
        cls.student = Student.objects.create(
            firstname='First',
            surname='Last',
        )
        cls.tutor = Tutor.objects.create(student=cls.student)
        cls.tutor_module = TutorModule.objects.create(module=cls.module, tutor=cls.tutor)
        cls.url = reverse('tutor-payment:quick:extras', kwargs={'pk': cls.tutor_module.pk})

        TutorFeeRate.objects.create(tag='online_extra_student', amount=20)
        TutorFeeRate.objects.create(tag='marking_rate', amount=6)
        cls.summative_rate = TutorFeeRate.objects.create(type='summative', amount=10, description='Summ')
        cls.formative_rate = TutorFeeRate.objects.create(type='formative', amount=10, description='Form')

    def setUp(self):
        self.client.force_login(self.user)

    def test_create_formative(self):
        response = self.client.post(
            self.url,
            data={
                'formative': 5,
                'formative_rate': self.formative_rate.pk,
                'approver': 'test',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(TutorFee.objects.last().approver, 'test')

    def test_create_summative(self):
        response = self.client.post(
            self.url,
            data={
                'summative': 5,
                'summative_rate': self.summative_rate.pk,
                'approver': 'test',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(TutorFee.objects.last().approver, 'test')

    def test_extra_students(self):
        response = self.client.post(
            self.url,
            data={
                'extra_students': 5,
                'approver': 'test',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(TutorFee.objects.last().approver, 'test')
