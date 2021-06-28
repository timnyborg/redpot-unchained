from django import forms

from . import models, passwords


class CreateForm(forms.ModelForm):
    class Meta:
        model = models.WebsiteAccount
        fields = ('username',)


class EditForm(forms.ModelForm):
    new_password = forms.CharField(
        widget=forms.PasswordInput(),
        help_text="Optional: replace the user's password",
        validators=[passwords.validate_password],
        required=False,
    )

    class Meta:
        model = models.WebsiteAccount
        fields = ('username', 'password', 'is_disabled')

    def __init__(self, edit_password: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not edit_password:
            del self.fields['password']
            del self.fields['new_password']
