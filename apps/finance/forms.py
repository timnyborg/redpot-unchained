from django import forms

from apps.core.utils.widgets import PoundInput

from . import models


class AddFeeForm(forms.ModelForm):
    submit_label = 'Add'
    type = forms.ModelChoiceField(
        queryset=models.TransactionType.objects.all(),
        limit_choices_to={'is_cash': False, 'is_active': True},
        error_messages={'blank': 'Required'},
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
        error_messages={'blank': 'Required'},
    )

    class Meta:
        model = models.Ledger
        fields = ('amount', 'narrative', 'type')
        widgets = {'amount': PoundInput()}
