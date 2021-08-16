from dal import autocomplete
from django_select2.forms import Select2MultipleWidget, Select2Widget

from django import forms
from django.core import exceptions
from django.forms import fields

from apps.core.utils import widgets
from apps.hesa.models import ModuleHECoSSubject
from apps.programme.models import ProgrammeModule

from . import models


class EditForm(forms.ModelForm):  # noqa: DJ06
    # todo: replace exclude
    class Meta:
        model = models.Module
        exclude = ['payment_plans']
        widgets = {
            'start_date': widgets.DatePickerInput(),
            'end_date': widgets.DatePickerInput(),
            'open_date': widgets.DatePickerInput(),
            'closed_date': widgets.DatePickerInput(),
            'publish_date': widgets.DatePickerInput(),
            'unpublish_date': widgets.DatePickerInput(),
            'michaelmas_end': widgets.DatePickerInput(),
            'hilary_start': widgets.DatePickerInput(),
            'subjects': Select2MultipleWidget(),
            'marketing_types': Select2MultipleWidget(),
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
