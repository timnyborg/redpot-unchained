from datetime import date

from django import test

from apps.core.utils.tests import LoggedInMixin
from apps.module.tests.factories import ModuleFactory
from apps.qualification_aim.tests.factories import QualificationAimFactory

from .. import models, services


class TestCreateEnrolment(LoggedInMixin, test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.module = ModuleFactory(start_date=date(2020, 1, 1))
        cls.qa = QualificationAimFactory()

    def test_create_sets_husid_and_startdate(self):
        """
        In addition to creating the enrolment, the service should set student.husid and qa.start_date
        """
        enrolment = services.create_enrolment(
            qa=self.qa,
            module=self.module,
            status=models.EnrolmentStatus.objects.get(pk=models.Statuses.CONFIRMED),
            user=self.user,
        )
        self.assertEqual(enrolment.qa, self.qa)
        self.qa.refresh_from_db()
        self.assertEqual(self.qa.start_date, self.module.start_date)
        self.assertIsInstance(self.qa.student.husid, int)
