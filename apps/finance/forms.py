from __future__ import annotations

from decimal import Decimal

from django import forms

from apps.core.utils.widgets import PoundInput
from apps.enrolment.models import Enrolment

from . import models


class AddFeeForm(forms.ModelForm):
    submit_label = 'Add'
    type = forms.ModelChoiceField(
        queryset=models.TransactionType.objects.all(),
        limit_choices_to={'is_cash': False, 'is_active': True},
    )

    class Meta:
        model = models.Ledger
        fields = ('amount', 'narrative', 'account', 'type')
        widgets = {'amount': PoundInput()}
        help_texts = {'amount': 'Positive values increase debt, negative decrease debt'}

    def __init__(self, editable_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not editable_type:
            self.fields['type'].widget = forms.HiddenInput()
            self.fields['type'].disabled = True


class AddPaymentForm(forms.ModelForm):
    submit_label = 'Add'
    type = forms.ModelChoiceField(
        queryset=models.TransactionType.objects.all(),
        limit_choices_to={'is_cash': True, 'is_active': True},
    )

    class Meta:
        model = models.Ledger
        fields = ('amount', 'narrative', 'type')
        widgets = {'amount': PoundInput()}


class MultipleEnrolmentPaymentForm(forms.Form):
    """Allows distributing a single payment between multiple enrolments.  Creates a field for every enrolment provided.
    Returns an `allocations` dict as part of `cleaned_data` for easy iteration over the results
    """

    submit_label = 'Add'

    amount = forms.DecimalField(widget=PoundInput(), label='Total paid')
    narrative = forms.CharField()
    type = forms.ModelChoiceField(queryset=models.TransactionType.objects.filter(is_cash=True, is_active=True))

    def clean(self):
        # Extract the allocation fields, and create a dictionary of {id: amount} for easy processing
        allocations: dict[int, Decimal] = {
            int(key.replace('allocation_', '')): val for key, val in self.cleaned_data.items() if 'allocation_' in key
        }
        self.cleaned_data['allocations'] = allocations

        # Ensure the total allocations matches the amount
        amount = self.cleaned_data.get('amount')
        allocated = sum(allocations.values())
        if amount and allocated != amount:
            self.add_error('amount', f'Does not match amount allocated below (£{allocated})')

    def __init__(self, enrolments: list[Enrolment], *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add an input row for every enrolment
        for enrolment in enrolments:
            fieldname = f'allocation_{enrolment.id}'
            self.fields[fieldname] = forms.DecimalField(
                label=f'{enrolment.module.code}',
                help_text=f'£{enrolment.get_balance():.2f} owing • {enrolment.module.title}',
                widget=PoundInput(),
            )


class TransferForm(forms.Form):
    submit_label = 'Transfer'

    target_enrolment = forms.ModelChoiceField(
        queryset=Enrolment.objects.all(),
        label='Transfer to',
    )
    amount = forms.DecimalField(
        min_value=0,
        error_messages={'min_value': 'Amount must be positive'},
        widget=PoundInput(),
    )
    narrative = forms.CharField()
    type = forms.ModelChoiceField(queryset=models.TransactionType.objects.filter(is_cash=True, is_active=True))

    def __init__(self, source_enrolment: Enrolment, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit target field to the student's other enrolments
        self.fields['target_enrolment'].queryset = (
            Enrolment.objects.filter(qa__student=source_enrolment.qa.student)
            .exclude(id=source_enrolment.id)
            .order_by('-module__start_date')
            .select_related('module')
        )
        # Easier than subclassing ModelChoiceField solely for this
        self.fields['target_enrolment'].label_from_instance = lambda obj: f'{obj.module} ({obj.module.code})'
