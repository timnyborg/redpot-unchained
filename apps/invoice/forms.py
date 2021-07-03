from django import forms
from django.core import validators

from apps.core.utils.widgets import DatePickerInput

from . import models


class LookupForm(forms.Form):
    number = forms.CharField(
        label='Number',
        validators=[validators.MinLengthValidator(3)],
        widget=forms.TextInput(attrs={'placeholder': 'e.g. EQ12345'}),
    )


class EditForm(forms.ModelForm):
    class Meta:
        model = models.Invoice
        fields = [
            'due_date',
            'invoiced_to',
            'fao',
            'line1',
            'line2',
            'line3',
            'town',
            'countystate',
            'country',
            'postcode',
            'ref_no',
            'vat_no',
            'contact_person',
            'contact_email',
            'contact_phone',
            'custom_narrative',
            'narrative',
        ]
        widgets = {'due_date': DatePickerInput()}
