from django import forms


class PushPaymentForm(forms.Form):
    submit_label = 'Push payment'
    payment_ref = forms.CharField(
        label='Payment reference', widget=forms.TextInput(attrs={'placeholder': 'a123bcd4e5f678'})
    )
    wpm_ref = forms.CharField(
        label='WPM reference',
        help_text='Used as the narrative in the ledger',
        widget=forms.TextInput(attrs={'placeholder': 'contCPG00001'}),
    )
