from datetime import date

from parameterized import parameterized

from django.test import SimpleTestCase, TestCase

from apps.enrolment.tests.factories import EnrolmentFactory
from apps.programme.tests.factories import ProgrammeFactory
from apps.tutor.tests.factories import TutorFactory

from .. import models, services
from . import factories
from .factories import PhoneFactory


class TestGenerateHUSID(SimpleTestCase):
    @parameterized.expand(
        [
            (1999, 12, 9911560000120),
            (2018, 9833, 1811560098335),
            (2020, 9300, 2011560093001),
        ]
    )
    def test_generation(self, year, seed, result):
        self.assertEqual(services._generate_husid(academic_year=year, seed=seed), result)


class TestGettingNextHUSID(TestCase):
    def test_model_creation_and_increment(self):
        """Check that a non-existant NextHUSID model will be generated when first required, with a 'next' of 0"""
        with self.assertRaises(models.NextHUSID.DoesNotExist):
            models.NextHUSID.objects.get(year=2021)
        services.next_husid(2021)
        self.assertEqual(models.NextHUSID.objects.get(year=2021).next, 1)
        services.next_husid(2021)
        self.assertEqual(models.NextHUSID.objects.get(year=2021).next, 2)

    def test_validation(self):
        self.assertRaises(ValueError, services.next_husid, 0)
        self.assertRaises(ValueError, services.next_husid, 9999)


class TestMerge(TestCase):
    def test_merging_tutors_raises_error(self):
        source, target = TutorFactory.create_batch(size=2)
        with self.assertRaisesRegex(services.merge.CannotMergeError, 'tutor'):
            services.merge.merge_students(source=source.student, target=target.student)

    def test_merging_sits_students_raises_error(self):
        source = factories.StudentFactory(sits_id=1)
        target = factories.StudentFactory(sits_id=2)
        with self.assertRaisesRegex(services.merge.CannotMergeError, 'SITS'):
            services.merge.merge_students(source=source, target=target)

    def test_merging_overrides_defaults(self):
        source = factories.StudentFactory(birthdate=date(2000, 1, 1), nationality_id=100)
        target = factories.StudentFactory(birthdate=None, nationality_id=models.NOT_KNOWN_NATIONALITY)

        services.merge._merge_properties(source=source, target=target)

        self.assertEqual(source.birthdate, target.birthdate)  # standard field
        self.assertEqual(source.nationality_id, target.nationality_id)  # notnull foreign key

    def test_merging_non_award_qas(self):
        """Enrolments should be moved"""
        programme = ProgrammeFactory(qualification_id=61)  # UG Credit
        source_enrolment = EnrolmentFactory(qa__programme=programme)
        target_enrolment = EnrolmentFactory(qa__programme=programme)

        services.merge._merge_qualification_aims(
            source=source_enrolment.qa.student, target=target_enrolment.qa.student
        )

        source_enrolment.refresh_from_db()
        self.assertEqual(source_enrolment.qa_id, target_enrolment.qa_id)

    def test_merging_award_qas(self):
        """Source QA should be moved"""
        programme = ProgrammeFactory(qualification_id=33)  # UG Cert
        source_enrolment = EnrolmentFactory(qa__programme=programme)
        target_enrolment = EnrolmentFactory(qa__programme=programme)

        services.merge._merge_qualification_aims(
            source=source_enrolment.qa.student, target=target_enrolment.qa.student
        )

        source_enrolment.refresh_from_db()
        self.assertNotEqual(source_enrolment.qa_id, target_enrolment.qa_id)
        self.assertEqual(source_enrolment.qa.student_id, target_enrolment.qa.student_id)

    def test_archiving(self):
        source, target = factories.StudentFactory.create_batch(size=2)
        result = services.merge._create_merge_archive_record(source=source, target=target)
        self.assertEqual(result.source, source.id)
        self.assertEqual(result.target, target.id)
        self.assertEqual(result.json['firstname'], source.firstname)

    def test_full_merge(self):
        """Check that the full merge method creates an archive and deletes the source student"""
        source, target = factories.StudentFactory.create_batch(size=2)
        PhoneFactory(student=source)
        PhoneFactory(student=target)
        TutorFactory(student=source)

        services.merge.merge_students(source=source, target=target)
        with self.assertRaises(models.Student.DoesNotExist):
            source.refresh_from_db()
        self.assertEqual(models.StudentArchive.objects.count(), 1)


class TestHUSIDSort(SimpleTestCase):
    def test_correct_order(self):
        no_husid = factories.StudentFactory.build(husid=None)
        _1999 = factories.StudentFactory.build(husid=9900000000000)
        _2005 = factories.StudentFactory.build(husid=500000000000)
        _2020 = factories.StudentFactory.build(husid=2000000000000)

        unordered = [_2005, no_husid, _2020, _1999]
        expected = [_1999, _2005, _2020, no_husid]
        self.assertEqual(sorted(unordered, key=services.merge._order_by_husid), expected)
