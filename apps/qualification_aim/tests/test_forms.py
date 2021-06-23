from django import test

from apps.programme.tests.factories import ProgrammeFactory
from apps.student.tests.factories import StudentFactory

from .. import forms
from . import factories

UG_CREDIT_QUALIFICATION = 61
NON_ACCREDITED_QUALIFICATION = 1


class TestCreateForm(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = StudentFactory()

    def test_hesa_returnable_programme_requires_entry_qual(self):
        programme = ProgrammeFactory(qualification_id=UG_CREDIT_QUALIFICATION)
        form = forms.CreateForm(
            data={
                'student': self.student,
                'programme': programme,
            }
        )
        self.assertIn('entry_qualification', form.errors)

    def test_non_returnable_programme_allows_empty_entry_qual(self):
        programme = ProgrammeFactory(qualification_id=NON_ACCREDITED_QUALIFICATION)
        form = forms.CreateForm(
            data={
                'student': self.student,
                'programme': programme,
            }
        )
        self.assertFalse(form.errors)


class TestEditForm(test.SimpleTestCase):
    def test_sits_code_disables_fields(self):
        qa = factories.QualificationAimFactory.build(sits_code=None)
        form = forms.EditForm(instance=qa)
        self.assertFalse(form.fields['start_date'].disabled)

        qa.sits_code = 'AB_123'
        form = forms.EditForm(instance=qa)
        self.assertTrue(form.fields['start_date'].disabled)
