from django import forms

from . import models


class CreateMoodleIDForm(forms.ModelForm):
    class Meta:
        model = models.MoodleID
        fields = ['student', 'moodle_id', 'first_module_code']
        widgets = {'student': forms.HiddenInput}


class MoodleIDForm(forms.ModelForm):
    class Meta:
        model = models.MoodleID
        fields = ['moodle_id', 'first_module_code']
