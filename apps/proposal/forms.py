from ckeditor.widgets import CKEditorWidget
from dal import autocomplete
from django_select2.forms import Select2MultipleWidget

from django import forms
from django.utils.safestring import mark_safe

from apps.core.utils import widgets
from apps.core.utils.forms import ApproverChoiceField
from apps.module.models import Equipment, Subject
from apps.proposal import models
from apps.tutor.models import Tutor, TutorModule

HTML_FIELDS = [
    'overview',
    'programme_details',
    'course_aims',
    'level_and_demands',
    'assessment_methods',
    'teaching_methods',
    'teaching_outcomes',
    'recommended_reading',
    'grammar_points',
    'tutor_biography',
]


class EditProposalForm(forms.ModelForm):
    michaelmas_end = forms.DateField(disabled=True, required=False)
    hilary_start = forms.DateField(disabled=True, required=False)
    dos = ApproverChoiceField(permission='proposal.approve_proposal', label='Director of studies', required=False)
    equipment = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.all(), required=False, widget=Select2MultipleWidget()
    )
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(), required=False, widget=Select2MultipleWidget()
    )

    class Meta:
        model = models.Proposal
        fields = [
            'status',
            'title',
            'tutor',
            'tutor_title',
            'tutor_nickname',
            'tutor_biography',
            'limited',
            'is_repeat',
            'start_date',
            'michaelmas_end',
            'hilary_start',
            'end_date',
            'start_time',
            'end_time',
            'no_meetings',
            'subjects',
            'duration',
            'location',
            'address',
            'room',
            'room_setup',
            'max_size',
            'reduced_size',
            'reduction_reason',
            'field_trips',
            'snippet',
            'overview',
            'programme_details',
            'course_aims',
            'level_and_demands',
            'assessment_methods',
            'teaching_methods',
            'teaching_outcomes',
            'image',
            'equipment',
            'scientific_equipment',
            'additional_requirements',
            'recommended_reading',
            'dos',
            'due_date',
            'grammar_points',
        ]
        widgets = {
            'tutor': widgets.ReadOnlyModelWidget(model=Tutor, link=True),
            **{field: CKEditorWidget for field in HTML_FIELDS},
            'start_date': widgets.DatePickerInput,
            'end_date': widgets.DatePickerInput,
            'due_date': widgets.DatePickerInput,
            'start_time': widgets.TimePickerInput,
            'end_time': widgets.TimePickerInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tutor'].disabled = True
        self.fields['status'].disabled = True

        # Highlight fields edited by tutor / dos
        for field in set(self.instance.updated_fields) & set(self.fields):  # ignore fields that aren't present
            # todo: do this with css class
            self.fields[field].label = mark_safe(
                f'<span class="text-primary fw-bold">{self.fields[field].label} (edited)</span>'
            )

    def clean(self) -> None:
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        # Check end_date is equal or later to start_date
        if end_date and not start_date:
            self.add_error('start_date', 'Please set a start date')
        if end_date and start_date and end_date < start_date:
            self.add_error('end_date', 'Cannot be earlier than start date')

        reduced_size = self.cleaned_data.get('reduced_size')
        reduction_reason = self.cleaned_data.get('reduction_reason')
        status = self.cleaned_data.get('status')
        if reduced_size:
            # Make reason specification obligatory
            if not reduction_reason:
                self.add_error('reduction_reason', 'Please specify reason for reduction')
            # If a reduced class size was filled the admin must move it to the real class size before completion
            if status == models.Statuses.ADMIN:
                self.add_error('reduced_size', 'Move value to class size or delete')
            # Any other status, make sure it's smaller than max
            elif reduced_size >= self.instance.max_size:
                self.add_error('reduced_size', 'Reduced size must be smaller than max size')

        # If scientific_equipment is ticked on make sure the specification is filled
        # todo: sort out '13' logic...
        equipment = self.cleaned_data.get('equipment')
        scientific_equipment = self.cleaned_data.get('scientific_equipment')
        if equipment:
            equipment_ids = [obj.pk for obj in equipment]
            if not scientific_equipment and 13 in equipment_ids:
                self.add_error('scientific_equipment', 'Please specify')
            elif scientific_equipment and 13 not in equipment_ids:
                self.cleaned_data['scientific_equipment'] = ''


class NewProposalForm(forms.ModelForm):
    submit_label = 'Create proposal'

    tutor_module = forms.ModelChoiceField(
        TutorModule.objects.all(),
        widget=autocomplete.ModelSelect2(url='autocomplete:tutor-on-module', attrs={'data-minimum-input-length': 3}),
        label='Tutor and module',
        help_text='Enter a module code or title, then select the tutor',
    )
    dos = ApproverChoiceField(
        permission='proposal.approve_proposal',
        label='Director of studies',
        error_messages={'required': 'Select a director of studies'},
    )

    class Meta:
        model = models.Proposal
        fields = ['tutor_module', 'dos', 'due_date', 'limited']
        widgets = {'due_date': widgets.DatePickerInput()}

    def clean(self):
        tutor_module = self.cleaned_data.get('tutor_module')
        if tutor_module and hasattr(tutor_module.module, 'proposal'):
            self.add_error('tutor_module', 'Proposal for selected module already exists')

        if tutor_module and not tutor_module.tutor.student.get_default_email():
            self.add_error('tutor_module', 'Selected tutor does not have an email address defined')
