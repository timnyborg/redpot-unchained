from datetime import date

from django import test

from apps.programme.tests.factories import ProgrammeFactory
from apps.student.tests.factories import StudentFactory

from .. import models
from . import factories


class TestSavingQualificationAimModel(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.programme = ProgrammeFactory(study_location_id=models.AT_PROVIDER_STUDY_LOCATION)
        cls.student = StudentFactory(highest_qualification_id='C20')

    def test_title_set_if_empty(self):
        qa = factories.QualificationAimFactory(programme=self.programme, title='Other')
        self.assertNotEqual(qa.title, self.programme.title)
        qa.title = None
        qa.save()
        self.assertEqual(qa.title, self.programme.title)

    def test_entry_qualification_set_if_empty(self):
        qa = factories.QualificationAimFactory(student=self.student, entry_qualification_id='C90')
        self.assertNotEqual(qa.entry_qualification_id, self.student.highest_qualification_id)
        qa.entry_qualification = None
        qa.save()
        self.assertEqual(qa.entry_qualification_id, self.student.highest_qualification_id)

    def test_non_uk_overseas_location(self):
        programme = ProgrammeFactory(study_location_id=models.UK_DISTANCE_STUDY_LOCATION)
        student = StudentFactory(domicile_id=181)
        qa = factories.QualificationAimFactory(student=student, programme=programme)
        self.assertEqual(qa.study_location_id, models.NON_UK_DISTANCE_STUDY_LOCATION)


class TestAcademicYear(test.SimpleTestCase):
    def test_null_if_null_start_date(self):
        qa = models.QualificationAim(start_date=None)
        self.assertIsNone(qa.academic_year)

    def test_academic_year(self):
        qa = models.QualificationAim(start_date=date(2020, 8, 1))
        self.assertEqual(qa.academic_year, 2020)
