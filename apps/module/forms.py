from django.forms import ModelForm, fields

from apps.programme.models import ProgrammeModule

from .models import Module


class EditForm(ModelForm):  # noqa: DJ06
    class Meta:
        model = Module
        exclude = ['payment_plans']


class CloneForm(ModelForm):
    # A dummy field to display data (may be a bad idea)
    source_module = fields.CharField(disabled=True)
    copy_fees = fields.BooleanField(
        label='Copy fee items',
        help_text='Fee amounts can be amended later',
        initial=True,
        required=False,
    )
    copy_books = fields.BooleanField(
        label='Copy reading list',
        help_text='Fee amounts can be amended later',
        initial=True,
        required=False,
    )
    copy_dates = fields.BooleanField(
        label='Copy course dates',
        help_text='Useful when creating a series of courses that occur on the same dates from a template, '
        'e.g. a summer school',
        initial=False,
        required=False,
    )
    keep_url = fields.BooleanField(
        label='Keep persistent URL',
        initial=True,
        required=False,
    )

    def __init__(self, remove_fields=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in remove_fields or []:
            del self.fields[field]

    class Meta:
        model = Module
        fields = ('source_module', 'code', 'title', 'is_repeat', 'copy_fees', 'copy_books', 'copy_dates', 'keep_url')


class CreateForm(ModelForm):
    class Meta:
        model = Module
        fields = ('code', 'title', 'division', 'portfolio', 'non_credit_bearing')


class AddProgrammeForm(ModelForm):
    class Meta:
        model = ProgrammeModule
        fields = ('programme',)
