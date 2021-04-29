from django import forms

from .models import Email, Student


class CreateEmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ('student', 'email', 'note')
        widgets = {'student': forms.HiddenInput}


class CreatePersonSearchForm(forms.ModelForm):
    birthdate = forms.DateField(required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = Student
        fields = ['surname', 'firstname', 'birthdate', 'email']
