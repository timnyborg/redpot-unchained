from django import forms
from django.core import validators

from apps.core.models import User
from apps.core.utils.forms import ApproverChoiceField


class UserForm(forms.ModelForm):
    username = forms.CharField(disabled=True, help_text='')
    default_approver = ApproverChoiceField(
        'tutor_payment.approve',
        required=False,
        help_text='This person will be pre-selected as the approver whenever you create a contract, '
        'finance change request, or tutor payment',
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'role', 'phone', 'room', 'image', 'default_approver')


class CreateUserForm(forms.ModelForm):
    username = forms.CharField(
        help_text="The user's departmental account username (e.g. SurnameF)",
        validators=[
            validators.MaxLengthValidator(8),
            validators.RegexValidator(r'^\w+$', message='This can only contain letters and numbers'),
        ],
    )

    class Meta:
        model = User
        fields = ('username',)
