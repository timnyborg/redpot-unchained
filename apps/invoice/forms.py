from django import forms
from django.core import validators


class InvoiceLookupForm(forms.Form):
    number = forms.CharField(
        label='Number',
        validators=[validators.MinLengthValidator(3)]
    )
