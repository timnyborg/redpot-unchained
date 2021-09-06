from django_select2.forms import Select2MultipleWidget

from django import forms

from apps.core.utils.widgets import DatePickerInput

from .models import Starter


class StarterForm(forms.ModelForm):
    class Meta:
        model = Starter

        fields = [
            'firstname',
            'lastname',
            'job_title',
            'email',
            'division',
            'systems',
            'start_date',
            'end_date',
            'is_a_member_of_TSS',
            'replacing',
            'telephone',
            'overseas_calls',
            'mailing_lists',
            'uni_card_number',
            'sso',
            'shared_accounts',
            'shared_folders',
            'others',
        ]

        widgets = {
            'systems': Select2MultipleWidget(),
            'mailing_lists': Select2MultipleWidget(),
            'start_date': DatePickerInput(),
            'end_date': DatePickerInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if end_date and start_date and (end_date < start_date):
            self.add_error('end_date', "End date should be greater than start date.")


class LeaverForm(forms.Form):
    CHOICES = (
        ('2 years', '2 Years'),
        ('6 years', '6 Years'),
    )

    firstname = forms.CharField(max_length=50)
    lastname = forms.CharField(max_length=50)
    sso = forms.CharField(max_length=50, label='SSO')
    leaving_date = forms.DateField(widget=DatePickerInput(format='%d/%m/%Y'))
    transfer_to = forms.CharField(label='Transfer data to', max_length=50, required=False)
    archive_for = forms.ChoiceField(label='Data retention', choices=CHOICES, required=False)
