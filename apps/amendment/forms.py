from dal.autocomplete import ModelSelect2

from django import forms
from django.urls import reverse_lazy
from django.utils.text import format_lazy

from apps.core.utils.forms import ApproverChoiceField
from apps.core.utils.strings import mark_safe_lazy
from apps.core.utils.widgets import PoundInput, ReadOnlyModelWidget
from apps.enrolment.models import Enrolment
from apps.invoice.models import Invoice
from apps.module.models import Module

from . import models


class BaseForm(forms.ModelForm):
    """Base class for common aspects of all amendment forms"""

    approver = ApproverChoiceField(
        'amendment.approve',
        help_text=mark_safe_lazy(
            format_lazy("Your default approver can be set in <a href='{}'>your profile</a>", reverse_lazy('user:edit'))
        ),
    )

    class Meta:
        first_fields, last_fields = ['enrolment', 'type', 'status', 'amount', 'reason'], [
            'details',
            'approver',
            'batch',
            'narrative',
            'is_complete',
        ]
        model = models.Amendment
        fields = first_fields + last_fields
        widgets = {
            'amount': PoundInput(),
            'enrolment': forms.HiddenInput(),
            'type': ReadOnlyModelWidget(model=models.AmendmentType),
            'status': ReadOnlyModelWidget(model=models.AmendmentStatus),
        }

    def __init__(self, edit_finance_fields: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].queryset = models.AmendmentReason.objects.filter(type=self.initial['type'])
        self.fields['reason'].empty_label = '– Choose one –'
        # Disable non-editable inputs
        for name in ('type', 'status', 'enrolment'):
            self.fields[name].disabled = True
        # Batch and narrative only editable by Finance (and when editing, in practice)
        if not edit_finance_fields:
            del self.fields['batch']
            del self.fields['narrative']
            del self.fields['is_complete']


class TransferForm(BaseForm):
    """The most complicated form, which allows transfers to another same-student enrolment, other-student enrolment,
    or between invoices.  todo: consider splitting this up"""

    source_invoice = forms.TypedChoiceField(coerce=int, widget=forms.Select(), required=False, empty_value=None)
    transfer_enrolment = forms.ModelChoiceField(
        queryset=Enrolment.objects.all(),
        widget=ModelSelect2('autocomplete:enrolment'),
        help_text='Enter the module code, then select a student',
        required=False,
    )

    class Meta(BaseForm.Meta):
        fields = (
            BaseForm.Meta.first_fields
            + ['transfer_module', 'transfer_enrolment', 'source_invoice', 'transfer_invoice']
            + BaseForm.Meta.last_fields
        )
        labels = {
            'reason': 'Transfer type',
            'details': 'Reason for transfer',
            'source_invoice': 'Source invoice/payment',
        }
        help_texts = {
            'details': 'You may also use this box for additional notes '
            'e.g. other students to receive element of transfer',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow modules the student is already enrolled on
        enrolment: Enrolment = self.instance.enrolment if self.instance.pk else self.initial['enrolment']
        other_modules = (
            Module.objects.filter(enrolment__qa__student=enrolment.qa.student)
            .exclude(enrolment__id=enrolment.id)
            .order_by('-start_date')
        )

        # creating transfer option list
        transfer_options = [
            (module.id, f'{module.code} - {module.title} ({module.start_date})') for module in other_modules
        ]

        if other_modules:
            # Add an option to specify multiple courses
            transfer_options.insert(0, ('', '– Choose one –'))
            transfer_options.append(('multiple', 'Multiple courses (specify below)'))
        else:
            transfer_options.insert(0, ('', 'No other enrolments found'))

        self.fields['transfer_module'] = forms.CharField(widget=forms.Select(choices=transfer_options), required=False)

        # Populate invoices and payments
        invoices = Invoice.objects.filter(ledger_items__enrolment=enrolment).distinct()
        self.fields['transfer_invoice'].queryset = invoices
        self.fields['transfer_invoice'].empty_label = '– Choose one –'

        payments = enrolment.ledger_set.debts().cash().filter(amount__lt=0).select_related('type')
        invoice_set = [(invoice.id, str(invoice)) for invoice in invoices]
        source_set = (
            invoice_set
            + [  # todo: this mixed foreign key is madness.  Attaching payments to invoices should be handled elsewhere
                (payment.id, f'{payment.narrative} ({payment.type.description}, £{-payment.amount:.2f})')
                for payment in payments
            ]
        )
        self.fields['source_invoice'].choices = [(None, '– Choose one –')] + source_set

    def clean(self):
        super().clean()
        # Ensure a the right details are set for a given reason.  # todo: rework to avoid hardcoded IDs
        if self.cleaned_data['reason'].id == 19 and not self.cleaned_data['transfer_module']:
            self.add_error('transfer_module', 'Required')
        if self.cleaned_data['reason'].id == 20 and not self.cleaned_data['transfer_enrolment']:
            self.add_error('transfer_enrolment', 'Required')
        if self.cleaned_data['reason'].id == 21 and not self.cleaned_data['source_invoice']:
            self.add_error('source_invoice', 'Required')
        if self.cleaned_data['reason'].id == 21 and not self.cleaned_data['transfer_invoice']:
            self.add_error('transfer_invoice', 'Required')


class AmendmentForm(BaseForm):
    invoice = forms.ModelChoiceField(queryset=Invoice.objects.all(), required=False, empty_label='– Optional –')

    class Meta(BaseForm.Meta):
        model = models.Amendment
        fields = BaseForm.Meta.first_fields + ['invoice'] + BaseForm.Meta.last_fields
        labels = {
            'reason': 'Amendment reason',
            'details': 'Amendment needed',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        enrolment = self.initial['enrolment']
        self.fields['invoice'].queryset = Invoice.objects.filter(ledger_items__enrolment=enrolment).distinct()


class RefundForm(BaseForm):
    """Simple change request form that handles multiple refund amendment types"""

    class Meta(BaseForm.Meta):
        model = models.Amendment
        fields = BaseForm.Meta.fields + ['actioned_online']
        labels = {
            'reason': 'Refund reason',
            'details': 'Additional details',
        }
        help_texts = {'details': 'Reminder: only pass credit card details to the finance officer by phone'}

    def __init__(self, edit_actioned_online=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not edit_actioned_online:
            del self.fields['actioned_online']
        if self.instance.type_id == models.AmendmentTypes.OTHER_REFUND:
            # todo: this is awkward.  Refunds should just have a shared set of reasons
            del self.fields['reason']
            del self.fields['approver']
