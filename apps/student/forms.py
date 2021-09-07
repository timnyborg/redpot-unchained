import re
from datetime import datetime

from dateutil.relativedelta import relativedelta
from ukpostcodeutils import validation

from django import forms
from django.core.exceptions import ValidationError

from apps.core.utils import widgets

from . import models


class CreateEmailForm(forms.ModelForm):
    class Meta:
        model = models.Email
        fields = ('student', 'email', 'note')
        widgets = {'student': forms.HiddenInput}


class CreatePersonSearchForm(forms.ModelForm):
    birthdate = forms.DateField(required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = models.Student
        fields = ['surname', 'firstname', 'birthdate', 'email']


class EditForm(forms.ModelForm):
    class Meta:
        model = models.Student
        fields = [
            'title',
            'firstname',
            'surname',
            'middlename',
            'nickname',
            'birthdate',
            'gender',
            'husid',
            'sits_id',
            'nationality',
            'domicile',
            'ethnicity',
            'religion_or_belief',
            'highest_qualification',
            'is_eu',
            'termtime_postcode',
            'disability',
            'disability_detail',
            'disability_action',
            'occupation',
            'deceased',
            'dars_optout',
            'is_flagged',
            'note',
        ]
        widgets = {
            'gender': forms.RadioSelect(attrs={'div_class': 'radio-inline'}),
            'is_eu': forms.RadioSelect(
                attrs={'div_class': 'radio-inline'},
                choices=((True, 'Yes'), (False, 'No'), (None, 'Unknown')),
            ),
            'birthdate': widgets.DatePickerInput(),
            'note': forms.Textarea(),
        }

    def clean_birthdate(self) -> None:
        """Prevent ages < 12 (arbitrary) to avoid common data entry errors (current date, 2067 instead of 1967, etc."""
        birthdate = self.cleaned_data['birthdate']
        if birthdate and birthdate > (datetime.today() - relativedelta(years=12)).date():
            self.add_error('birthdate', 'Must be a bit older than that!')


class AddressForm(forms.ModelForm):
    country = forms.ModelChoiceField(
        queryset=models.Domicile.objects.all(),
        limit_choices_to={'is_active': True},
        to_field_name='name',
        empty_label=' – Select – ',
        error_messages={'required': 'Please select a country'},
    )

    class Meta:
        model = models.Address
        fields = [
            'type',
            'line1',
            'line2',
            'line2',
            'town',
            'countystate',
            'country',
            'postcode',
            'is_default',
            'is_billing',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable any SITS-managed fields
        for field in self.instance.locked_fields.intersection(self.fields):
            self.fields[field].disabled = True
        # Unsetting 'is_default' doesn't make sense as an action
        if self.instance.is_default:
            del self.fields['is_default']

    def clean_postcode(self) -> str:
        """If country is in the UK, validates a UK postcode, and reformats it to uppercase with the correct space"""
        country = self.cleaned_data.get('country')
        postcode = self.cleaned_data.get('postcode')
        if postcode and country and 'United Kingdom' in country.name:
            spaceless_postcode = re.sub(r'\s', '', postcode).upper()
            if not validation.is_valid_postcode(spaceless_postcode):
                raise ValidationError('Invalid UK postcode')
            postcode = f'{spaceless_postcode[:-3]} {spaceless_postcode[-3:]}'

        return postcode
