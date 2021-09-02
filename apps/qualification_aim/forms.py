from django import forms
from django.core.exceptions import ValidationError

from . import models


class CreateForm(forms.ModelForm):
    class Meta:
        model = models.QualificationAim
        fields = ['programme', 'entry_qualification']

    def clean(self):
        # Require entry qualifications for hesa-returnable programmes
        programme = self.cleaned_data.get('programme')
        if programme and programme.qualification.on_hesa_return and not self.cleaned_data.get('entry_qualification'):
            raise ValidationError({'entry_qualification': "Required.  Choose 'Not known' if unknown"})


class EditForm(forms.ModelForm):
    # Todo: permissions-based field access
    class Meta:
        model = models.QualificationAim
        fields = (
            'title',
            'start_date',
            'end_date',
            'study_location',
            'reason_for_ending',
            'sits_code',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable any SITS-managed fields
        for field in self.instance.locked_fields.intersection(self.fields):
            self.fields[field].disabled = True


class CertHEMarksForm(forms.ModelForm):
    class Meta:
        model = models.CertHEMarks
        fields = [
            'courses_transferred_in',
            'credits_transferred_in',
            'subject',
            'assignment1_date',
            'assignment1_grade',
            'assignment2_date',
            'assignment2_grade',
            'assignment3_date',
            'assignment3_grade',
            'journal1_date',
            'journal2_date',
            'journal_cats_points',
            'is_introductory_course',
        ]
