from django import forms

from apps.module.models import Module

from . import models


class AccommodationForm(forms.ModelForm):
    class Meta:
        model = models.Accommodation
        fields = ['type', 'note', 'limit']


class CateringForm(forms.ModelForm):
    class Meta:
        model = models.Catering
        fields = ['fee']

    def __init__(self, module: Module, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # limits options to the module's catering fees
        self.fields['fee'].queryset = module.fees.filter(is_catering=True)
        self.fields['fee'].label = 'Catering option'
