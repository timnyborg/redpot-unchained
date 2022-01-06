from dal import autocomplete

from django import forms
from django.core.exceptions import ValidationError

from apps.core.utils.widgets import ReadOnlyModelWidget
from apps.student.models import Student

from . import models


class WaitlistForm(forms.ModelForm):
    submit_label = 'Add to waiting list'

    class Meta:
        model = models.Waitlist
        fields = ['student', 'module']
        widgets = {
            'student': ReadOnlyModelWidget(model=Student),
            'module': autocomplete.ModelSelect2(url='autocomplete:module', attrs={'data-minimum-input-length': 3}),
        }

    def clean(self):
        student = self.cleaned_data.get('student')
        module = self.cleaned_data.get('module')
        if student and module and student.qualification_aims.filter(enrolment__module=module).exists():
            raise ValidationError({'module': 'Student already enrolled on module'})
