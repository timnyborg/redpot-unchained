from django.forms import ModelForm
from django.urls import reverse_lazy
from django.utils.text import format_lazy

from apps.core.utils.strings import mark_safe_lazy
from apps.core.utils.widgets import PoundInput

from .models import Fee


class FeeForm(ModelForm):
    """Used for both create and edit"""

    class Meta:
        model = Fee
        fields = (
            'amount',
            'type',
            'description',
            'eu_fee',
            'is_visible',
            'is_payable',
            'is_catering',
            'is_single_accom',
            'is_twin_accom',
            'credit_fee',
            'end_date',
            'allocation',
            'limit',
        )
        widgets = {'amount': PoundInput()}
        help_texts = {
            'limit': mark_safe_lazy(
                format_lazy("<a href='{}' target='_blank'>Manage limits</a>", reverse_lazy('booking:limit-search'))
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['limit'].empty_label = ' - None - '
