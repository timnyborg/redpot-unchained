from django import forms
from django.db import models

from apps.core.utils.widgets import DatePickerInput


class BrochureTypes(models.TextChoices):
    PROSPECTUS = 'Prospectus', 'Annual prospectus'
    NEWSPAPER = 'Newspaper', 'Public programmes newspaper'
    SUBJECT_AREA_BROCHURES = 'Subject area brochures', 'Subject area brochures'
    __empty__ = ' – Select – '


class ExportXMLForm(forms.Form):
    submit_label = 'XMĹ!'
    starting_from = forms.DateField(label='Courses starting from', widget=DatePickerInput())
    brochure_type = forms.ChoiceField(
        choices=BrochureTypes.choices, error_messages={'required': 'Please choose a brochure type'}
    )
