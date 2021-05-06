from django.forms import ModelForm

from .models import Fee


class FeeForm(ModelForm):
    """Used for both create and edit"""

    class Meta:
        model = Fee
        fields = (
            'amount',
            'type',
            'description',
            'allocation',
            'eu_fee',
            'is_visible',
            'is_payable',
            'is_catering',
            'is_single_accom',
            'is_twin_accom',
            'credit_fee',
            'end_date',
            'limit',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['limit'].empty_label = ' - None - '
