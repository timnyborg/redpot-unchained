from django import forms
from django.core.exceptions import ValidationError

from apps.core.utils.forms import SITSLockingFormMixin

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


class EditForm(SITSLockingFormMixin, forms.ModelForm):
    # Todo: permissions-based field access for sits_code
    class Meta:
        model = models.QualificationAim
        fields = (
            'title',
            'start_date',
            'end_date',
            'study_location',
            'entry_qualification',
            'reason_for_ending',
            'sits_code',
        )


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
