from dal import autocomplete

from django import forms
from django.core import exceptions

from . import models


class ProgrammeEditForm(forms.ModelForm):
    class Meta:
        model = models.Programme
        fields = [
            'title',
            'division',
            'portfolio',
            'qualification',
            'email',
            'phone',
            'student_load',
            'funding_level',
            'funding_source',
            'study_mode',
            'study_location',
            'is_active',
            'contact_list_display',
            'sits_code',
        ]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user
        # dynamically readonly a field
        # self.fields['title'].disabled = True

        # dynamically remove a field
        if not user.has_perm('registry'):
            for f in ['student_load', 'funding_level', 'funding_source', 'study_mode', 'study_location']:
                del self.fields[f]

        if not user.has_perm('programme.edit_restricted_fields'):
            for f in ['is_active', 'contact_list_display', 'sits_code']:
                del self.fields[f]


class ProgrammeNewForm(forms.ModelForm):
    class Meta:
        model = models.Programme
        fields = ['title', 'qualification', 'division', 'portfolio', 'sits_code']


class AttachModuleForm(forms.ModelForm):
    programme = forms.ModelChoiceField(
        queryset=models.Programme.objects.all(),
        disabled=True,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = models.ProgrammeModule
        fields = ['programme', 'module']
        widgets = {
            'module': autocomplete.ModelSelect2(url='autocomplete:module', attrs={'data-minimum-input-length': 3})
        }
        error_messages = {
            exceptions.NON_FIELD_ERRORS: {'unique_together': 'The module is already attached to the programme'}
        }
