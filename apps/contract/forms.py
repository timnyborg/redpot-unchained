from django import forms
from django.core import validators
from django.db.models import TextChoices
from django.template import loader
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.text import format_lazy

from apps.contract import models
from apps.core.utils.forms import ApproverChoiceField
from apps.core.utils.strings import mark_safe_lazy
from apps.core.utils.widgets import DatePickerInput, PoundInput


class ReturnAddresses(TextChoices):
    REWLEY = 'Rewley House, 1 Wellington Square, OX1 2JA', 'Rewley House, 1 Wellington Square, OX1 2JA'
    EWERT = 'Ewert House, Ewert Place, Summertown, OX2 7DD', 'Ewert House, Ewert Place, Summertown, OX2 7DD'


SUPERVISOR_CHOICES = [
    ('', '– Please select –'),
    ('Director of Studies', 'Director of Studies'),
    ('Programme Director', 'Programme Director'),
    ('Deputy Director', 'Deputy Director'),
    ('Module Coordinator', 'Module Coordinator'),
]
PAYMENT_FREQUENCY_CHOICES = [
    ('', '– Please select –'),
    ('monthly in arrears', 'monthly in arrears'),
    ('termly in arrears', 'termly in arrears'),
    ('on completion of the delivery of your teaching', 'on completion of the delivery of your teaching'),
]


class ContractForm(forms.ModelForm):
    """Base class for the tailored contract forms, with shared definitions and logic"""

    approver = ApproverChoiceField(
        'contract.approve_contract',
        help_text=mark_safe_lazy(
            format_lazy("Your default approver can be set in <a href='{}'>your profile</a>", reverse_lazy('user:edit'))
        ),
    )
    # Common option fields
    phone = forms.CharField(
        label='Contact phone',
        validators=[validators.RegexValidator(regex='^[-0-9 +()]+$', message='Invalid phone number')],
    )
    email = forms.EmailField(label='Contact email')
    venue = forms.CharField(help_text='e.g. Ewert House')
    return_to = forms.CharField(help_text='The name of the administrator or team')
    return_address = forms.ChoiceField(choices=ReturnAddresses.choices, initial=ReturnAddresses.REWLEY)

    class Meta:
        model = models.Contract
        fields = ['approver', 'email_notification']

    @property
    def extra_cleaned_data(self) -> dict:
        """Extract non-model data for ease of serialization"""
        fieldnames = [field.name for field in models.Contract._meta.get_fields()]
        out = {k: v for k, v in self.cleaned_data.items() if k not in fieldnames}
        return out


class CasualTeachingForm(ContractForm):
    start_date = forms.DateField(widget=DatePickerInput())
    end_date = forms.DateField(widget=DatePickerInput())
    supervisor = forms.CharField(
        help_text='The person overseeing the tutor, responsible for approving any substitutes'
    )
    supervisor_role = forms.ChoiceField(choices=SUPERVISOR_CHOICES, label="Supervisor's role")
    rate_of_pay = forms.CharField(
        validators=[validators.RegexValidator(r'^.*£', 'Please enter a rate in £s')],
        help_text=loader.render_to_string('contract/components/rate_of_pay_help_text.html'),
    )
    payment_frequency = forms.ChoiceField(
        choices=PAYMENT_FREQUENCY_CHOICES,
        help_text='Will the tutor be paid monthly, termly, or in a lump sum after the course?',
    )
    payment_preconditions = forms.CharField(
        help_text='Optional. Specify whether there are any other preconditions for payment, '
        'e.g. submission of online student reports.',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
    )
    expected_work = forms.CharField(
        help_text=mark_safe(
            "A short summary of the work, e.g. 'You will be required to teach weekly lectures, direct class "
            "discussion, and mark assignments.'  <b>If you wish to provide extensive detail, attach a schedule "
            "of work.</b>"
        ),
        widget=forms.Textarea(attrs={'rows': 3}),
    )
    attached_work = forms.BooleanField(
        label='Schedule of work attached?',
        help_text='Will a schedule/description of the work be attached?',
        required=False,
        initial=True,
    )
    references_required = forms.BooleanField(
        help_text='Is this contract subject to the provision of references?',
        required=False,
    )

    field_order = [
        'start_date',
        'end_date',
        'phone',
        'email',
        'venue',
        'supervisor',
        'supervisor_role',
        'approver',
        'rate_of_pay',
        'payment_frequency',
        'payment_preconditions',
        'expected_work',
        'attached_work',
        'references_required',
        'return_to',
        'return_address',
        'email_notification',
    ]

    def clean_expected_work(self):
        return self.cleaned_data['expected_work'].strip('.')


class GuestSpeakerForm(ContractForm):
    topic = forms.CharField(label='Lecture topic(s)')
    dates_and_times = forms.CharField(
        help_text=mark_safe('When the lectures will take place. E.g. <i>12 Jan 2020 at 9:45, 11:15, and 13:30</i>'),
    )
    lecture_no = forms.IntegerField(label='Number of lectures', initial=1, min_value=1, max_value=100)
    fee_per_lecture = forms.DecimalField(
        max_digits=8, decimal_places=2, max_value=10000, min_value=0, widget=PoundInput()
    )

    field_order = [
        'phone',
        'email',
        'topic',
        'venue',
        'dates_and_times',
        'lecture_no',
        'fee_per_lecture',
        'approver',
        'return_to',
        'return_address',
        'email_notification',
    ]
