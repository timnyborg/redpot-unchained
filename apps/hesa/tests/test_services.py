from parameterized import parameterized

from django import test

from apps.enrolment.tests.factories import EnrolmentFactory
from apps.module.tests.factories import ModuleFactory
from apps.programme.tests.factories import ProgrammeFactory
from apps.qualification_aim.tests.factories import QualificationAimFactory
from apps.student.tests.factories import StudentFactory

from .. import models, services

INSTITUTIONAL_CREDIT_QUALIFICATION = 61
CONFIRMED_STATUS = 10
ENGLAND_DOMICILE = 240
PASSED_RESULT = 1


class TestCompletionField(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.incomplete = EnrolmentFactory(result_id=services.INCOMPLETE_RESULT)
        cls.unknown = EnrolmentFactory(result_id=services.UNKNOWN_RESULT)
        cls.passed = EnrolmentFactory(result_id=services.PASS_RESULT)
        cls.failed = EnrolmentFactory(result_id=services.FAIL_RESULT)

    def test_incomplete(self):
        enrolments = [
            self.incomplete,
            self.unknown,
            self.passed,
            self.failed,
        ]
        self.assertEqual(services._completion(enrolments=enrolments), 2)

    def test_unknown(self):
        enrolments = [
            self.unknown,
            self.passed,
            self.failed,
        ]
        self.assertEqual(services._completion(enrolments=enrolments), 3)

    def test_complete(self):
        enrolments = [
            self.passed,
            self.failed,
        ]
        self.assertEqual(services._completion(enrolments=enrolments), 1)


class TestReasonForEnding(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.incomplete = EnrolmentFactory(result_id=services.INCOMPLETE_RESULT)
        cls.unknown = EnrolmentFactory(result_id=services.UNKNOWN_RESULT)
        cls.passed = EnrolmentFactory(result_id=services.PASS_RESULT)
        cls.failed = EnrolmentFactory(result_id=services.FAIL_RESULT)

    def test_incomplete(self):
        enrolments = [
            self.incomplete,
            self.unknown,
            self.failed,
        ]
        self.assertEqual(services._reason_for_ending(enrolments=enrolments), '02')

    def test_unknown(self):
        enrolments = [
            self.incomplete,
            self.unknown,
            self.passed,
            self.failed,
        ]
        self.assertEqual(services._reason_for_ending(enrolments=enrolments), '01')


class TestPostcode(test.SimpleTestCase):
    @parameterized.expand(
        [
            ('ox12ja', 'OX1 2JA'),
            ('ox33 2ja', 'OX33 2JA'),
            (' o x12ja ', 'OX1 2JA'),
            ('S7N 2L7', services.EMPTY_ELEMENT),
            ('12345', services.EMPTY_ELEMENT),
        ]
    )
    def test_postcode_filter(self, postcode, expected):
        self.assertEqual(services._correct_postcode(postcode), expected)


class TestReturnProduction(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        """Create a hesa-returnable student record"""
        cls.programme = ProgrammeFactory(qualification_id=INSTITUTIONAL_CREDIT_QUALIFICATION)
        cls.student = StudentFactory(domicile_id=ENGLAND_DOMICILE, ethnicity=1)  # todo: convert once model implemented
        cls.qa = QualificationAimFactory(
            student=cls.student,
            programme=cls.programme,
        )
        cls.module = ModuleFactory(credit_points=10, start_date='2021-01-01')
        cls.enrolment = EnrolmentFactory(
            qa=cls.qa, module=cls.module, status_id=CONFIRMED_STATUS, result_id=PASSED_RESULT
        )

    def test_return_includes_enrolment(self):
        # todo: add in course & module subjects
        hesa_return = services.HESAReturn(2020, 'test')
        hesa_return.create()

        self.assertEqual(models.StudentOnModule.objects.count(), 1)

        student_on_module = models.StudentOnModule.objects.first()
        self.assertEqual(
            student_on_module.modid,
            self.module.code,
        )

    def test_xml_contains_all_datatypes(self):
        self.maxDiff = None
        # todo: add in course & module subjects
        hesa_return = services.HESAReturn(2020, 'test')
        batch = hesa_return.create()

        xml = services._generate_tree(batch.id)
        # todo: add subjects once implemented
        for element in [
            '<Course>',
            '<Module>',
            '<EntryProfile>',
            '<Student>',
            '<StudentOnModule>',
            '<Instance>',
            '<QualificationsAwarded>',
        ]:
            self.assertIn(element, xml)

    # todo: add no-result test cases, etc.
