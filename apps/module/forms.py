from dal import autocomplete

from django import forms
from django.core import exceptions
from django.forms import fields

from apps.core.utils import widgets
from apps.programme.models import ProgrammeModule

from . import models


class EditForm(forms.ModelForm):  # noqa: DJ06
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
        }


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
