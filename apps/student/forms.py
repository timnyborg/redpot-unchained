from django import forms

from .models import Email


class CreateEmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ('student', 'email', 'note')
        widgets = {'student': forms.HiddenInput}
