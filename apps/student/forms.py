from django import forms

from .models import Email, Student


class CreateEmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ('student', 'email', 'note')
        widgets = {'student': forms.HiddenInput}

class StudentSearchForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ('firstname', 'surname', 'birthdate')
