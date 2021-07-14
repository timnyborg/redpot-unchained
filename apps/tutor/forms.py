from dal import autocomplete

from django.forms import ModelForm
from django.utils.safestring import mark_safe

from apps.core.utils.widgets import DatePickerInput, ReadOnlyModelWidget
from apps.module.models import Module

from .models import RightToWorkType, Tutor, TutorModule


class BasicEdit(ModelForm):
    """Basic form for users lacking bank details rights"""

    class Meta:
        model = Tutor
        fields = [
            'qualifications',
            'affiliation',
            'biography',
            'image',
        ]


class Edit(ModelForm):
    """Full form for users with bank details rights"""

    class Meta:
        model = Tutor
        fields = [
            'qualifications',
            'affiliation',
            'nino',
            'employee_no',
            'appointment_id',
            'bankname',
            'branchaddress',
            'accountname',
            'sortcode',
            'accountno',
            'swift',
            'iban',
            'other_bank_details',
            'biography',
            'image',
            'oracle_supplier_number',
        ]


class RightToWork(ModelForm):
    # todo: document_type as an autocomplete
    # (https://django-autocomplete-light.readthedocs.io/en/master/tutorial.html#filtering-results-based-on-the-value-of-other-fields-in-the-form)
    class Meta:
        model = Tutor
        fields = ['rtw_type', 'rtw_document_type', 'rtw_check_on', 'rtw_check_by', 'rtw_start_date', 'rtw_end_date']
        widgets = {
            'rtw_start_date': DatePickerInput(),
            'rtw_end_date': DatePickerInput(),
            'rtw_check_on': DatePickerInput(),
        }

    def clean(self):
        rtw_type = self.cleaned_data.get('rtw_type')
        document_type = self.cleaned_data.get('rtw_document_type')
        start_date = self.cleaned_data.get('rtw_start_date')
        end_date = self.cleaned_data.get('rtw_end_date')

        if rtw_type in (RightToWorkType.PERMANENT, RightToWorkType.LIMITED):
            if not document_type:
                self.add_error('rtw_document_type', 'Required')
            # Check that document type is a subset of type (if necessary)
            elif document_type.rtw_type != rtw_type:
                self.add_error('rtw_document_type', 'Invalid document')
        else:
            self.cleaned_data['rtw_document_type'] = None

        if rtw_type == RightToWorkType.LIMITED:
            # Document start and end date required for list B
            if not start_date:
                self.add_error('rtw_start_date', 'Required for List B')
            if not end_date:
                self.add_error('rtw_end_date', 'Required for List B')
            if start_date and end_date and start_date > end_date:
                self.add_error('rtw_end_date', 'Must be later than date of issue')
        else:
            # But not for anything else
            self.cleaned_data['rtw_start_date'] = None
            self.cleaned_data['rtw_end_date'] = None


class TutorModuleEditForm(ModelForm):
    class Meta:
        model = TutorModule
        fields = [
            'role',
            'is_published',
            'is_teaching',
            'director_of_studies',
            'biography',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add a link to the tutor's global biography
        bio_link = self.instance.tutor.student.get_absolute_url() + '#tutor'
        self.fields['biography'].help_text = mark_safe(
            f'When filled, this overrides <a href="{bio_link}">the default tutor biography</a> for this module only'
        )


class TutorModuleCreateForm(ModelForm):
    class Meta:
        model = TutorModule
        fields = [
            'module',
            'tutor',
            'role',
            'is_published',
            'is_teaching',
            'director_of_studies',
            'biography',
        ]
        widgets = {
            'module': autocomplete.ModelSelect2(
                url='autocomplete:module',
                attrs={'data-minimum-input-length': 3},
            ),
            'tutor': autocomplete.ModelSelect2(
                url='autocomplete:tutor',
                attrs={'data-minimum-input-length': 3},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lock fields with initial values
        module = kwargs['initial'].get('module')
        tutor = kwargs['initial'].get('tutor')
        if module:
            self.fields['module'].widget = ReadOnlyModelWidget(Module)
        if tutor:
            self.fields['tutor'].widget = ReadOnlyModelWidget(Tutor)
