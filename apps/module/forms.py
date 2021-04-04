from django.forms import ModelForm

from .models import Module


class EditForm(ModelForm):  # noqa: DJ06
    class Meta:
        model = Module
        exclude = ['payment_plans']


class CreateForm(ModelForm):
    class Meta:
        model = Module
        fields = ('code', 'title', 'division', 'portfolio', 'non_credit_bearing')
