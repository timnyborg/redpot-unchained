from django import forms


class BatchPrintForm(forms.Form):
    submit_label = 'Create batch'
    level = forms.ChoiceField(
        choices=(('', ' – Select – '), ('undergraduate', 'Undergraduate'), ('postgraduate', 'Postgraduate'))
    )
    header = forms.BooleanField(
        label='University header?', widget=forms.RadioSelect(choices=((True, 'Yes'), (False, 'No')))
    )
