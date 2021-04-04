from django.core import validators
from django.db import models
from django.forms import widgets


class UpperCaseCharField(models.CharField):
    """Automatically upper-cases the input
    It's unclear if it's better to use the customized field, or to do the work in .save()
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, str):
            return value.upper()
        return str(value).upper()


class PhoneInput(widgets.TextInput):
    input_type = 'tel'


class PhoneField(models.CharField):
    default_validators = [validators.RegexValidator(regex='^[-0-9 +()]+$', message='Invalid phone number')]
    widget = PhoneInput
