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
