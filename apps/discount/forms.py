from django import forms

from apps.core.utils import widgets
from apps.discount import models


class DiscountForm(forms.ModelForm):
    class Meta:
        model = models.Discount
        fields = ['name', 'code', 'percent', 'expires_on', 'module_mask', 'portfolio']
        widgets = {'expires_on': widgets.DatePickerInput(), 'percent': widgets.PercentInput()}
