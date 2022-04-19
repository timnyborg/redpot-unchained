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


class RequestSiteForm(forms.Form):
    title = forms.CharField()
    start_date = forms.DateField()
    access_start_date = forms.DateField(label='Student first access date')
    end_date = forms.DateField()
    access_end_date = forms.DateField(label='Student last access date')
    online_submission = forms.BooleanField(label='Course includes online submission?', required=False)
    admin = forms.CharField(label='Course admin name')
    email = forms.EmailField(label='Course admin email')
    backup_email = forms.EmailField(
        label='Backup email',
        help_text='If the admin email is for a personal email account, provide a backup address for holiday cover',
        required=False,
    )
    type = forms.ChoiceField(
        choices=[('', '– Select –'), ('Existing', 'Existing'), ('New', 'New')], label='Course type'
    )
    url = forms.URLField(required=False, help_text="Existing course's moodle URL")
