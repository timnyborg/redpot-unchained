from datetime import datetime

from dateutil.relativedelta import relativedelta

from django import forms
from django.utils.safestring import mark_safe

from apps.core.utils.widgets import DatePickerInput
from apps.module.models import Module
from apps.qualification_aim.models import QualificationAim
from apps.student.models import Student

from . import models


class ModuleChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        # Custom rendering, rather than Module's __str__
        return f'{obj.title} – {obj.code} ({obj.start_date})'


class CreateForm(forms.Form):
    module = ModuleChoiceField(
        Module.objects.order_by('title', '-start_date').exclude(is_cancelled=True),
        label='Module',
        help_text='Showing all courses on this programme',
    )
    enrolment_fields = forms.fields_for_model(models.Enrolment)
    status = enrolment_fields['status']

    def __init__(self, *, qa: QualificationAim, missing_student_fields: list, limit_modules=True, **kwargs):
        super().__init__(**kwargs)
        # dynamically filter module options based on the programme
        module_queryset = self.fields['module'].queryset.filter(programme=qa.programme)
        # limit modules to recent
        if limit_modules:
            module_queryset = module_queryset.filter(start_date__gt=datetime.today() - relativedelta(months=3))
            self.fields['module'].help_text = mark_safe(
                'Showing recent and future courses on this programme. <a href="?all=true">Show all</a>'
            )
        self.fields['module'].queryset = module_queryset

        # dynamically add fields for missing student attributes
        student_fields = forms.fields_for_model(
            model=Student,
            fields=missing_student_fields,
            widgets={'birthdate': DatePickerInput()},  # type: ignore
        )
        self.fields.update(**student_fields)

    def clean(self):
        # Disallow enrolling on full 'weekly classes' (portfolio=32) programs. Other workflows are more forgiving.
        # TODO: replace with portfolio flags
        module = self.cleaned_data.get('module')
        if module and module.portfolio_id == 32 and module.is_full():
            self.add_error('module', 'Module is full')
