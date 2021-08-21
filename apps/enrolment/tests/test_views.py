from datetime import date

from freezegun import freeze_time

from django import test
from django.urls import reverse

from apps.core.utils.tests import LoggedInViewTestMixin
from apps.fee.tests.factories import FeeFactory
from apps.finance.services import add_enrolment_fee
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
                'religion_or_belief': self.qa.student.religion_or_belief,
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
