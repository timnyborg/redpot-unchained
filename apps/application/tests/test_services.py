from django import test

from apps.core.tests.factories import UserFactory
from apps.module.tests.factories import ModuleFactory
from apps.programme.tests.factories import ProgrammeFactory

from .. import services
from . import factories


class TestCreateStudent(test.TestCase):
    def test_create_with_child_records(self):
        application = factories.ApplicationFactory(student=None, email_optin=True, post_optin=True)
        user = UserFactory()

        student = services.create_student_from_application(application=application, user=user)

        self.assertEqual(application.firstname, student.firstname)
        self.assertEqual(application.phone, student.phones.first().number)
        self.assertEqual(application.email, student.emails.first().email)


class TestCreateEnrolment(test.TestCase):
    def test_create(self):
        # Attach the module to a programme so a qa can be created
        module = ModuleFactory()
        module.programmes.add(ProgrammeFactory())
        application = factories.ApplicationFactory(module=module)
        user = UserFactory()

        enrolment = services.enrol_applicant(application=application, user=user)

        self.assertEqual(enrolment.qa.student, application.student)
        self.assertEqual(enrolment.module, application.module)
