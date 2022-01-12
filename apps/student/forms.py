from __future__ import annotations

import re
from datetime import date, datetime
from typing import Optional

from dateutil.relativedelta import relativedelta
from ukpostcodeutils.validation import is_valid_postcode

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError

from apps.core.utils import widgets
from apps.core.utils.forms import SITSLockingFormMixin

from . import models


class CreateEmailForm(forms.ModelForm):
    class Meta:
        model = models.Email
        fields = ('student', 'email', 'note', 'is_default')
        widgets = {'student': forms.HiddenInput}


class EmailForm(SITSLockingFormMixin, forms.ModelForm):
    class Meta:
        model = models.Email
        fields = ('email', 'note', 'is_default')


class CreatePersonSearchForm(forms.ModelForm):
    birthdate = forms.DateField(required=False, widget=widgets.DatePickerInput())
    email = forms.EmailField(required=False)

    class Meta:
        model = models.Student
        fields = ['surname', 'firstname', 'birthdate', 'email']


class EditForm(SITSLockingFormMixin, forms.ModelForm):
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
            'sexual_orientation',
            'parental_education',
            'gender_identity',
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
            'title': widgets.DatalistTextInput(options=['Miss', 'Mr', 'Mrs', 'Ms', 'Mx', 'Dr', 'Prof', 'Rev', 'Fr']),
            'gender': forms.RadioSelect(attrs={'div_class': 'form-check-inline'}),
            'is_eu': forms.RadioSelect(
                attrs={'div_class': 'form-check-inline'},
                choices=((True, 'Yes'), (False, 'No'), (None, 'Unknown')),
            ),
            'birthdate': widgets.DatePickerInput(),
            'note': forms.Textarea(),
        }

    def __init__(self, edit_restricted_fields: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # dynamically remove a field
        if not edit_restricted_fields:
            for f in ['sexual_orientation', 'parental_education', 'gender_identity']:
                del self.fields[f]

    def clean_birthdate(self) -> Optional[date]:
        """Prevent ages < 12 (arbitrary) to avoid common data entry errors (current date, 2067 instead of 1967, etc."""
        birthdate = self.cleaned_data['birthdate']
        if birthdate and birthdate > (datetime.today() - relativedelta(years=12)).date():
            raise ValidationError('Must be a bit older than that!')
        return birthdate


class AddressForm(SITSLockingFormMixin, forms.ModelForm):
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
        # Unsetting 'is_default' doesn't make sense as an action
        if self.instance.is_default:
            del self.fields['is_default']

    def clean_postcode(self) -> str:
        """If country is in the UK, validates a UK postcode, and reformats it to uppercase with the correct space"""
        country = self.cleaned_data.get('country')
        postcode = self.cleaned_data.get('postcode')
        if postcode and country and 'United Kingdom' in country.name:
            spaceless_postcode = re.sub(r'\s', '', postcode).upper()
            if not is_valid_postcode(spaceless_postcode):
                raise ValidationError('Invalid UK postcode')
            postcode = f'{spaceless_postcode[:-3]} {spaceless_postcode[-3:]}'

        return postcode


class CreatePhoneForm(forms.ModelForm):
    class Meta:
        model = models.Phone
        fields = ['student', 'number', 'type', 'note', 'is_default']
        widgets = {'student': forms.HiddenInput}


class PhoneForm(SITSLockingFormMixin, forms.ModelForm):
    class Meta:
        model = models.Phone
        fields = ['number', 'type', 'note', 'is_default']


class CreateOtherIDForm(forms.ModelForm):
    class Meta:
        model = models.OtherID
        fields = ['student', 'number', 'type', 'note', 'start_date', 'end_date']
        widgets = {
            'student': forms.HiddenInput,
            'start_date': widgets.DatePickerInput(),
            'end_date': widgets.DatePickerInput(),
        }


class OtherIDForm(SITSLockingFormMixin, forms.ModelForm):
    class Meta:
        model = models.OtherID
        fields = ['number', 'type', 'note', 'start_date', 'end_date']
        widgets = {
            'start_date': widgets.DatePickerInput(),
            'end_date': widgets.DatePickerInput(),
        }


class CreateMoodleIDForm(forms.ModelForm):
    class Meta:
        model = models.MoodleID
        fields = ['student', 'moodle_id', 'first_module_code']
        widgets = {'student': forms.HiddenInput}


class MoodleIDForm(forms.ModelForm):
    class Meta:
        model = models.MoodleID
        fields = ['moodle_id', 'first_module_code']


class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = models.EmergencyContact
        fields = ['name', 'phone', 'email']


class MergeForm(forms.Form):
    records = forms.ModelMultipleChoiceField(
        queryset=models.Student.objects.none(),
        label='Records',
        widget=forms.CheckboxSelectMultiple(),
        validators=[validators.MinLengthValidator(2, message='Please select at least two records')],
    )

    def __init__(self, record_ids: list[int], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['records'].label_from_instance = lambda obj: f'{obj.firstname} {obj.surname} ({obj.husid})'
        self.fields['records'].queryset = models.Student.objects.filter(pk__in=record_ids)


class MarketingForm(forms.ModelForm):
    submit_label = 'Submit'
    hide_delete_button = True

    class Meta:
        model = models.Student
        fields = [
            'email_optin',
            'email_optin_on',
            'email_optin_method',
            'mail_optin',
            'mail_optin_on',
            'mail_optin_method',
            'no_publicity',
        ]
        widgets = {
            'student': forms.HiddenInput,
            'mail_optin_on': widgets.DateTimePickerInput(),
            'email_optin_on': widgets.DateTimePickerInput(),
            'email_optin': widgets.ToggleWidget(
                attrs={
                    'data-on': 'Opted in',
                    'data-off': 'Not opted in',
                    'data-onstyle': 'success',
                    'data-offstyle': 'secondary',
                }
            ),
            'mail_optin': widgets.ToggleWidget(
                attrs={
                    'data-on': 'Opted in',
                    'data-off': 'Not opted in',
                    'data-onstyle': 'success',
                    'data-offstyle': 'secondary',
                }
            ),
            'no_publicity': widgets.ToggleWidget(
                attrs={
                    'data-on': 'Opted out',
                    'data-off': 'Not opted-out',
                    'data-onstyle': 'danger',
                    'data-offstyle': 'secondary',
                }
            ),
        }

    def clean_marketing(self):
        cleaned_data = super().clean()
        email_optin = cleaned_data.get("email_optin")
        email_optin_method = cleaned_data.get("email_optin_method")
        email_optin_on = cleaned_data.get("email_optin_on")
        mail_optin = cleaned_data.get("mail_optin")
        mail_optin_method = cleaned_data.get("mail_optin_method")
        mail_optin_on = cleaned_data.get("mail_optin_on")

        # Require details fields
        if email_optin:
            if not email_optin_method:
                self.add_error('email_optin_method', 'Required')
            if not email_optin_on:
                self.add_error('email_optin_on', 'Required')

        # Same for mail
        if mail_optin:
            if not mail_optin_method:
                self.add_error('mail_optin_method', 'Required')
            if not mail_optin_on:
                self.add_error('mail_optin_on', 'Required')
