from datetime import date

from freezegun import freeze_time

from django import test

from apps.module.tests.factories import ModuleFactory
from apps.programme.tests.factories import ProgrammeFactory
from apps.qualification_aim.tests.factories import QualificationAimFactory
from apps.student.services import EMPTY_ATTRIBUTE_VALUES

from .. import forms, models


@freeze_time(date(2020, 1, 1))
class TestCreateForm(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.programme = ProgrammeFactory()
        cls.qa = QualificationAimFactory(programme=cls.programme)
        # Mixture of modules which should appear as options or not
        cls.future_module = ModuleFactory(start_date=date(2020, 2, 1))
        cls.future_module.programmes.add(cls.programme)
        cls.past_module = ModuleFactory(start_date=date(2000, 1, 1))
        cls.past_module.programmes.add(cls.programme)
        cls.non_programme_module = ModuleFactory()

    def test_only_shows_modules_on_programme(self):
        """Module options should exclude modules on other programmes"""
        form = forms.CreateForm(
            qa=self.qa,
            missing_student_fields=[],
            limit_modules=False,
        )
        modules = form.fields['module'].queryset.all()
        self.assertEqual(len(modules), 2)
        self.assertIn(self.past_module, modules)
        self.assertNotIn(self.non_programme_module, modules)

    def test_limited_modules(self):
        form = forms.CreateForm(
            qa=self.qa,
            missing_student_fields=[],
            limit_modules=True,
        )
        modules = form.fields['module'].queryset.all()
        self.assertEqual(len(modules), 1)
        self.assertIn(self.future_module, modules)
        self.assertNotIn(self.past_module, modules)

    def test_missing_student_fields(self):
        form = forms.CreateForm(
            qa=self.qa,
            missing_student_fields=EMPTY_ATTRIBUTE_VALUES.keys(),
        )
        self.assertIn('birthdate', form.fields)

    def test_full_error(self):
        self.future_module.max_size = -1  # hackish way to make is_full = True
        self.future_module.portfolio_id = 32  # todo: replace with a portfolio tag once those are built
        self.future_module.save()

        form = forms.CreateForm(
            qa=self.qa,
            missing_student_fields=[],
            data={
                'module': self.future_module,
                'status': models.Statuses.CONFIRMED,
            },
        )
        self.assertTrue(any('full' in error for error in form.errors['module']))
