from django import forms

from apps.core.models import User
from apps.core.utils.forms import ApproverChoiceField


class UserForm(forms.ModelForm):
    default_approver = ApproverChoiceField(
        'tutor_payment.approve',
        required=False,
        help_text='This person will be pre-selected as the approver whenever you create a contract, '
        'finance change request, or tutor payment',
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'role', 'phone', 'room', 'image', 'default_approver')
