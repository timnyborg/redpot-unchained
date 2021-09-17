from ckeditor.widgets import CKEditorWidget
from dal import autocomplete
from django_select2.forms import Select2MultipleWidget, Select2Widget

from django import forms
from django.core import exceptions
from django.forms import fields
from django.forms.widgets import Textarea

from apps.core.utils import widgets
from apps.hesa.models import ModuleHECoSSubject
from apps.programme.models import ProgrammeModule

from . import models

HTML_FIELDS = [
    'overview',
    'accommodation',
    'how_to_apply',
    'assessment_methods',
    'certification',
    'course_aims',
    'level_and_demands',
    'libraries',
    'payment',
    'programme_details',
    'recommended_reading',
    'scholarships',
    'snippet',
    'teaching_methods',
    'teaching_outcomes',
    'selection_criteria',
    'it_requirements',
    'further_details',
]
DATE_FIELDS = [
    'start_date',
    'end_date',
    'open_date',
    'publish_date',
    'unpublish_date',
    'michaelmas_end',
    'hilary_start',
]


class EditForm(forms.ModelForm):  # noqa: DJ06
    # todo: replace exclude
    class Meta:
        model = models.Module
        fields = [
            'code',
            'title',
            'url',
            'division',
            'portfolio',
            'format',
            'phone',
            'email',
            'subjects',
            'marketing_types',
            'non_credit_bearing',
            'default_non_credit',
            'start_date',
            'half_term',
            'end_date',
            'start_time',
            'end_time',
            'meeting_time',
            'open_date',
            'closed_date',
            'publish_date',
            'unpublish_date',
            'location',
            'max_size',
            'single_places',
            'twin_places',
            'address',
            'no_meetings',
            'week_number',
            'cost_centre',
            'activity_code',
            'source_of_funds',
            'custom_fee',
            'snippet',
            'notification',
            'overview',
            'programme_details',
            'selection_criteria',
            'course_aims',
            'certification',
            'assessment_methods',
            'it_requirements',
            'level_and_demands',
            'recommended_reading',
            'teaching_methods',
            'teaching_outcomes',
            'accommodation',
            'payment',
            'scholarships',
            'how_to_apply',
            'further_details',
            'terms_and_conditions',
            'enrol_online',
            'apply_url',
            'no_search',
            'mailing_list',
            'image',
            'credit_points',
            'points_level',
            'note',
            'direct_enrolment',
        ]
        widgets = {
            'closed_date': widgets.DateTimePickerInput(),
            'subjects': Select2MultipleWidget(),
            'marketing_types': Select2MultipleWidget(),
            'non_credit_bearing': widgets.ToggleWidget(
                attrs={
                    'data-on': 'Non-credit',
                    'data-off': 'For credit',
                    'data-onstyle': 'warning',
                    'data-offstyle': 'success',
                }
            ),
            'default_non_credit': widgets.ToggleWidget(
                attrs={
                    'data-on': 'Non-credit',
                    'data-off': 'For credit',
                    'data-offstyle': 'success',
                    'data-onstyle': 'warning',
                }
            ),
            'enrol_online': widgets.ToggleWidget(attrs={'data-on': 'Allowed', 'data-off': 'Not allowed'}),
            'direct_enrolment': widgets.ToggleWidget(attrs={'data-on': 'Allowed', 'data-off': 'Not allowed'}),
            'note': Textarea(),
            'notification': CKEditorWidget(config_name='links_only'),
            **{field: CKEditorWidget() for field in HTML_FIELDS},
            **{field: widgets.DatePickerInput() for field in DATE_FIELDS},
            'start_time': widgets.TimePickerInput(),
            'end_time': widgets.TimePickerInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subjects'].label_from_instance = lambda obj: f'{obj.name} ({obj.area})'


class LookupForm(forms.Form):
    module = forms.IntegerField(
        widget=autocomplete.ListSelect2(
            url='autocomplete:module',
            attrs={'data-minimum-input-length': 3, 'data-placeholder': 'Enter a module title or code'},
        ),
    )


class CloneForm(forms.ModelForm):
    # A dummy field to display data (may be a bad idea)
    source_module = fields.CharField(disabled=True)
    copy_fees = fields.BooleanField(
        label='Copy fee items',
        help_text='Fee amounts can be amended later',
        initial=True,
        required=False,
    )
    copy_books = fields.BooleanField(
        label='Copy reading list',
        help_text='Fee amounts can be amended later',
        initial=True,
        required=False,
    )
    copy_dates = fields.BooleanField(
        label='Copy course dates',
        help_text='Useful when creating a series of courses that occur on the same dates from a template, '
        'e.g. a summer school',
        initial=False,
        required=False,
    )
    keep_url = fields.BooleanField(
        label='Keep persistent URL',
        initial=True,
        required=False,
    )

    def __init__(self, remove_fields=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in remove_fields or []:
            del self.fields[field]

    class Meta:
        model = models.Module
        fields = ('source_module', 'code', 'title', 'is_repeat', 'copy_fees', 'copy_books', 'copy_dates', 'keep_url')


class CopyFeesForm(forms.Form):
    submit_label = 'Copy fees'
    source_module = forms.ModelChoiceField(
        models.Module.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='autocomplete:module',
            attrs={'data-minimum-input-length': 3},
        ),
        label='Source module',
        help_text='Copy all fees from this module',
    )


class CopyFieldsForm(forms.Form):
    submit_label = 'Copy fields'
    source_module = forms.ModelChoiceField(
        models.Module.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='autocomplete:module',
            attrs={'data-minimum-input-length': 3},
        ),
        label='Source module',
        help_text='Copy web fields from this module (overview, programme details, etc.)',
    )


class CreateForm(forms.ModelForm):
    class Meta:
        model = models.Module
        fields = ('code', 'title', 'division', 'portfolio', 'non_credit_bearing')


class AddProgrammeForm(forms.ModelForm):
    module = forms.ModelChoiceField(
        queryset=models.Module.objects.all(),
        disabled=True,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = ProgrammeModule
        fields = ['programme', 'module']
        error_messages = {
            exceptions.NON_FIELD_ERRORS: {'unique_together': 'The module is already attached to the programme'}
        }


class HESASubjectForm(forms.ModelForm):
    class Meta:
        model = ModuleHECoSSubject
        fields = ['hecos_subject', 'percentage']
        widgets = {'hecos_subject': Select2Widget()}


class BaseHESASubjectFormSet(forms.BaseInlineFormSet):
    """Adds validation to the HESA subject formset"""

    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        total_percentage = sum(
            form.cleaned_data.get('percentage', 0) for form in self.forms if not self._should_delete_form(form)
        )
        # Don't raise an error if the total is 0 (all rows deleted)
        if total_percentage not in (0, 100):
            raise exceptions.ValidationError(f"Percentages add to {total_percentage}, not 100")


HESASubjectFormSet = forms.inlineformset_factory(
    parent_model=models.Module,
    model=ModuleHECoSSubject,
    form=HESASubjectForm,
    formset=BaseHESASubjectFormSet,
    max_num=3,
    validate_max=True,
)
