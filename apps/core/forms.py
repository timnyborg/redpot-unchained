from dal_select2.widgets import Select2

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from apps.core import models


class CustomAuthForm(AuthenticationForm):
    """A custom Login form & view to enable overriding error_messages"""

    error_messages = {
        'invalid_login': "Please enter your departmental %(username)s and password",
        'inactive': "This account is inactive.",
    }


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj: models.User) -> str:
        return f'{obj.get_full_name()} ({obj.username})'


class ImpersonateForm(forms.Form):
    user_pk = UserChoiceField(
        queryset=models.User.objects.order_by('last_name', 'first_name'), widget=Select2(), label='User'
    )
