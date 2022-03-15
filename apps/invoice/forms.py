from django import forms
from django.core import validators
from django.forms.models import fields_for_model

from apps.core.utils.widgets import DatePickerInput, PoundInput
from apps.enrolment.models import Enrolment
from apps.finance.models import Ledger, TransactionType
from apps.student.models import Student

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

    class Media:
        js = ('js/invoice_form.js',)


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


class CreditForm(forms.Form):
    submit_label = 'Add credit'
    enrolment = forms.ModelChoiceField(queryset=Enrolment.objects.all())
    account = fields_for_model(Ledger)['account']
    amount = forms.DecimalField(widget=PoundInput(), help_text='Positive values decrease debt, negative increase debt')
    narrative = forms.CharField()
    type = forms.ModelChoiceField(queryset=TransactionType.objects.filter(is_cash=False, is_active=True))

    def __init__(self, invoice: models.Invoice, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit the enrolments to those connected with the invoice
        self.fields['enrolment'].queryset = (
            Enrolment.objects.filter(ledger__invoice=invoice).distinct().select_related('module').order_by('-id')
        )
        # Dropdown options display the module title
        self.fields['enrolment'].label_from_instance = lambda obj: obj.module


class SelectForPaymentForm(forms.Form):
    submit_label = 'Select invoice'
    invoice = forms.ModelChoiceField(queryset=models.Invoice.objects.all(), empty_label=' – Select – ')

    def __init__(self, student: Student, exclude_paid: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = student.get_invoices().order_by('-id')
        if exclude_paid:
            qs = qs.outstanding()
        self.fields['invoice'].queryset = qs
        self.fields['invoice'].label_from_instance = lambda obj: f'{obj} (£{obj.balance:.2f})'


class PaymentForm(forms.Form):
    submit_label = 'Add payment'
    enrolment = forms.ModelChoiceField(
        queryset=Enrolment.objects.all(),
        required=False,
        empty_label=' – All – ',
    )
    amount = forms.DecimalField(widget=PoundInput())
    narrative = forms.CharField()
    type = forms.ModelChoiceField(queryset=TransactionType.objects.filter(is_cash=True, is_active=True))

    def __init__(self, invoice: models.Invoice, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit the enrolments to those connected with the invoice
        self.fields['enrolment'].queryset = (
            Enrolment.objects.filter(ledger__invoice=invoice).distinct().select_related('module').order_by('-id')
        )
        # Dropdown options display the module title
        self.fields[
            'enrolment'
        ].label_from_instance = lambda obj: f'{obj.module.code} - {obj.module} (£{obj.get_balance():.2f})'
