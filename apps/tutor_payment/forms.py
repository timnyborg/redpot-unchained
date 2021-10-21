from typing import Optional

from django import forms
from django.core import validators
from django.db import transaction
from django.forms import ValidationError
from django.forms.models import fields_for_model

from apps.core.utils import widgets
from apps.core.utils.forms import ApproverChoiceField
from apps.core.utils.widgets import PoundInput

from . import models


class PaymentForm(forms.ModelForm):
    """Form for creating or editing a payment"""

    approver = ApproverChoiceField('tutor_payment.approve')

    class Meta:
        model = models.TutorPayment
        fields = [
            'type',
            'status',
            'hourly_rate',
            'hours_worked',
            'amount',
            'weeks',
            'details',
            'approver',
            'pay_after',
        ]
        widgets = {
            'hourly_rate': widgets.PoundInput(),
            'amount': widgets.PoundInput(),
            'pay_after': widgets.MonthPickerInput(),
        }

    def __init__(self, editable_status: Optional[bool] = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].disabled = not editable_status


class ExtrasForm(forms.Form):
    formative = forms.DecimalField(min_value=0, max_value=100, decimal_places=1, required=False)
    formative_rate = forms.ModelChoiceField(
        models.PaymentRate.objects.filter(type='formative'),
        required=False,
    )
    summative = forms.DecimalField(min_value=0, max_value=100, decimal_places=1, required=False)
    summative_rate = forms.ModelChoiceField(
        models.PaymentRate.objects.filter(type='summative'),
        required=False,
    )
    extra_students = forms.IntegerField(
        label='Extra online students',
        min_value=0,
        max_value=100,
        help_text='At £%.2f per extra enrolment',
        required=False,
    )
    approver = fields_for_model(models.TutorPayment)['approver']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamic help-text
        per_student = models.PaymentRate.objects.lookup('online_extra_student')
        self.fields['extra_students'].help_text %= per_student

    def clean(self):
        """Do form-wide validation"""
        data = self.cleaned_data
        errors = {}

        summative = self.cleaned_data.get('summative')
        summative_rate = self.cleaned_data.get('summative_rate')
        formative = self.cleaned_data.get('formative')
        formative_rate = self.cleaned_data.get('formative_rate')

        # Ensure a rate is chosen if a summative # is provided, and vice versa
        if summative and not summative_rate:
            errors['summative_rate'] = 'Required'
        if not summative and summative_rate:
            errors['summative'] = 'Required'
        if formative and not formative_rate:
            errors['formative_rate'] = 'Required'
        if not formative and formative_rate:
            errors['formative'] = 'Required'
        if not any(val for key, val in data.items() if key != 'approver'):
            # non-field error, rendered at the top
            self.add_error(None, 'Choose at least one payment type')

        if errors:
            raise ValidationError(errors)

    @transaction.atomic
    def create_record(self, tutor_module, user):
        """Create payments from the form data, supplemented with tutor_module and user from the view"""

        # todo: this really should be in a service, not in a form
        # Lookup current rates
        marking_hourly = models.PaymentRate.objects.lookup('marking_rate')
        per_student = models.PaymentRate.objects.lookup('online_extra_student')

        # Concise variable names for the form data
        formative = self.cleaned_data['formative']
        formative_rate = self.cleaned_data['formative_rate']
        summative = self.cleaned_data['summative']
        summative_rate = self.cleaned_data['summative_rate']
        extra_students = self.cleaned_data['extra_students']
        approver = self.cleaned_data['approver']

        # Add each type of payment, if we've specified it on the form
        if formative:
            amount = formative * formative_rate.amount
            models.TutorPayment.create_with_holiday(
                tutor_module=tutor_module,
                amount=amount,
                payment_type_id=models.Types.EXAMINING,
                details=f'Marking (Formative, {formative} @ £{formative_rate.amount:.2f})',
                approver=approver,
                hourly_rate=marking_hourly,
                weeks=1,
                raised_by=user,
            )

        if summative:
            amount = summative * summative_rate.amount
            models.TutorPayment.create_with_holiday(
                tutor_module=tutor_module,
                amount=amount,
                payment_type_id=models.Types.EXAMINING,
                details=f'Marking (Summative, {summative} @ £{summative_rate.amount:.2f})',
                approver=approver,
                hourly_rate=marking_hourly,
                weeks=1,
                raised_by=user,
            )

        if extra_students:
            amount = extra_students * per_student
            models.TutorPayment.create_with_holiday(
                tutor_module=tutor_module,
                amount=amount,
                payment_type_id=models.Types.TEACHING,
                details=f'Extra students payment ({extra_students})',
                approver=approver,
                hourly_rate=marking_hourly,
                weeks=1,
                raised_by=user,
            )


# Making choices work with complex objects is a bit tricky: the choices stores the array indices, which are used
# to fetch the schedule in Form.clean().  Could be done in a custom field type?
schedule_choices = [(i, schedule.label) for i, schedule in enumerate(models.schedules)]


class OnlineTeachingForm(forms.Form):
    amount = forms.ModelChoiceField(models.PaymentRate.objects.filter(type='online_teaching'))
    schedule = forms.TypedChoiceField(choices=schedule_choices, coerce=int)
    approver = ApproverChoiceField('tutor_payment.approve')

    def clean(self) -> None:
        self.cleaned_data['schedule'] = models.schedules[self.cleaned_data['schedule']]


class WeeklyTeachingForm(forms.Form):
    rate = forms.DecimalField(max_digits=10, decimal_places=4, widget=PoundInput(), disabled=True, label='Hourly rate')
    length = forms.DecimalField(
        max_digits=10,
        decimal_places=1,
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(100)],
        label='Hours per week (prep & teaching)',
        help_text='Typically 4 for in-person, 5 for online',
    )
    no_meetings = forms.IntegerField(
        validators=[validators.MinValueValidator(1), validators.MaxValueValidator(21)],
        label='Number of meetings',
    )
    schedule = forms.TypedChoiceField(choices=schedule_choices, coerce=int)
    approver = ApproverChoiceField('tutor_payment.approve')

    def clean(self) -> None:
        self.cleaned_data['schedule'] = models.schedules[self.cleaned_data['schedule']]
