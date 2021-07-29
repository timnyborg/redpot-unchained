from django import forms
from django.core import validators

from apps.core.utils.widgets import DatePickerInput, PoundInput

from . import models


class LookupForm(forms.Form):
    number = forms.CharField(
        label='Number',
        validators=[validators.MinLengthValidator(3)],
        widget=forms.TextInput(attrs={'placeholder': 'e.g. EQ12345'}),
    )


class InvoiceForm(forms.ModelForm):
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


class UploadRCPForm(forms.Form):
    submit_label = 'Upload payments'
    file = forms.FileField(
        validators=[validators.FileExtensionValidator(['csv'])],
        widget=forms.FileInput(attrs={'accept': '.csv'}),
        help_text='A payments .csv file from WPM',
    )


class PaymentPlanForm(forms.ModelForm):
    """Used for both creating and updating payment plans"""

    invoice = forms.ModelChoiceField(
        queryset=models.Invoice.objects.all(),
        widget=forms.HiddenInput(),
        disabled=True,
    )

    class Meta:
        model = models.PaymentPlan
        fields = ('invoice', 'type', 'status', 'amount')
        help_texts = {'status': "If plan already exists, choose 'Payment schedule active'"}
        widgets = {'amount': PoundInput()}
