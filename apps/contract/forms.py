from django import forms
from django.core import validators
from django.utils.safestring import mark_safe

from apps.contract import models
from apps.core.utils.forms import ApproverChoiceField

RETURN_ADDRESS_CHOICES = (
    ('Rewley House, 1 Wellington Square, OX1 2JA', 'Rewley House, 1 Wellington Square, OX1 2JA'),
    ('Ewert House, Ewert Place, Summertown, OX2 7DD', 'Ewert House, Ewert Place, Summertown, OX2 7DD'),
)
EXPENSE_CHOICES = [
    ('45p', 'Standard expenses text (45p/mi.)'),
    ('33p', 'Undergraduate text (33p/mi.)'),
]
SUPERVISOR_CHOICES = [
    ('Director of Studies', 'Director of Studies'),
    ('Programme Director', 'Programme Director'),
    ('Deputy Director', 'Deputy Director'),
    ('Module Coordinator', 'Module Coordinator'),
    ('', '– Please select –'),
]
PAYMENT_FREQUENCY_CHOICES = [
    ('monthly in arrears', 'monthly in arrears'),
    ('termly in arrears', 'termly in arrears'),
    ('on completion of the delivery of your teaching', 'on completion of the delivery of your teaching'),
    ('', '– Please select –'),
]


class ContractForm(forms.ModelForm):
    """Base class for the tailored contract forms, with shared definitions and logic"""

    approver = ApproverChoiceField('contract.approve', help_text='Your default approver can be set in your profile')

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
    phone = forms.CharField(
        label='Contact phone',
        validators=[validators.RegexValidator(regex='^[-0-9 +()]+$', message='Invalid phone number')],
    )
    email = forms.EmailField(label='Contact email')
    return_to = forms.CharField(help_text='The name of the administrator or team')
    return_address = forms.ChoiceField(choices=RETURN_ADDRESS_CHOICES)
    venue = forms.CharField(help_text='e.g. Ewert House')
    expense_details = forms.ChoiceField(
        choices=EXPENSE_CHOICES,
        label='Travel expense details',
        help_text='Which travel expense rate to include in the standard text',
    )
    supervisor = forms.CharField(
        help_text='The person overseeing the tutor, responsible for approving any substitutes'
    )
    supervisor_role = forms.ChoiceField(choices=SUPERVISOR_CHOICES, label="Supervisor's role")
    rate_of_pay = forms.CharField(
        validators=[validators.RegexValidator(r'^.*£', 'Please enter a rate in £s')],
        # todo: move to a template?
        help_text=mark_safe(
            """
                <a class="pull-right" href="#"
                     data-toggle='modal'
                     data-target='#calculator-modal'
                ><span class="fa fa-calculator"></span> Calculator</a>
                <b>Excluding</b> holiday pay.
                <br/>E.g. <i>£20/hr</i>.
                <br/>or <i>£100/day (at a notional rate of £20/hr)</i>
                <br/>
                For more complicated payment situations, use an attached schedule of work.
            """
        ),
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
    )
    references_required = forms.BooleanField(
        label='Schedule of work attached?',
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
        'expense_details',
        'return_to',
        'return_address',
        'email_notification',
    ]
