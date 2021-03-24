from django import forms
from django.forms import ValidationError
from django.forms.models import fields_for_model
from django.db import transaction

from .models import TutorFeeRate, TutorFee


class ExtrasForm(forms.Form):
    formative = forms.DecimalField(min_value=0, max_value=100, decimal_places=1, required=False)
    formative_rate = forms.ModelChoiceField(
        TutorFeeRate.objects.filter(type='formative'),
        required=False,
        to_field_name='amount'
    )
    summative = forms.DecimalField(min_value=0, max_value=100, decimal_places=1, required=False)
    summative_rate = forms.ModelChoiceField(
        TutorFeeRate.objects.filter(type='summative'),
        required=False,
        to_field_name='amount'
    )
    extra_students = forms.IntegerField(
        label='Extra online students',
        min_value=0, max_value=100,
        help_text='At £%.2f per extra enrolment',
        required=False,
    )
    approver = fields_for_model(TutorFee)['approver']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamic help-text
        per_student = TutorFeeRate.objects.lookup('online_extra_student')
        self.fields['extra_students'].help_text %= per_student

    def clean(self):
        """Do form-wide validation"""
        data = self.cleaned_data
        errors = {}

        # Ensure a rate is chosen if a summative # is provided, and vice versa
        if data['summative'] and not data['summative_rate']:
            errors['summative_rate'] = 'Required'
        if not data['summative'] and data['summative_rate']:
            errors['summative'] = 'Required'
        if data['formative'] and not data['formative_rate']:
            errors['formative_rate'] = 'Required'
        if not data['formative'] and data['formative_rate']:
            errors['formative'] = 'Required'
        if not any(val for key, val in data.items() if key != 'approver'):
            # non-field error, rendered at the top
            self.add_error(None, 'Choose at least one fee type')

        if errors:
            raise ValidationError(errors)

    @transaction.atomic
    def create_record(self, tutor_module, user):
        """Create payments from the form data, supplemented with tutor_module and user from the view"""

        # Lookup current rates
        marking_hourly = TutorFeeRate.objects.lookup('marking_rate')
        per_student = TutorFeeRate.objects.lookup('online_extra_student')

        # Concise variable names for the form data
        formative = self.cleaned_data['formative']
        formative_rate = self.cleaned_data['formative_rate']
        summative = self.cleaned_data['summative']
        summative_rate = self.cleaned_data['summative_rate']
        extra_students = self.cleaned_data['extra_students']
        approver = self.cleaned_data['approver']

        # Add each type of fee, if we've specified it on the form
        if formative:
            amount = formative * formative_rate.amount
            TutorFee.create_with_holiday(
                tutor_module=tutor_module,
                amount=amount,
                fee_type_id=4,  # Examining.  todo: use a choices object
                details=f'Marking (Formative, {formative} @ £{formative_rate.amount:.2f})',
                approver=approver,
                hourly_rate=marking_hourly,
                weeks=1,
                raised_by=user.username
            )

        if summative:
            amount = summative * summative_rate.amount
            TutorFee.create_with_holiday(
                tutor_module=tutor_module,
                amount=amount,
                fee_type_id=4,  # Examining.  todo: use a choices object
                details=f'Marking (Summative, {summative} @ £{summative_rate.amount:.2f})',
                approver=approver,
                hourly_rate=marking_hourly,
                weeks=1,
                raised_by=user.username
            )

        if extra_students:
            amount = extra_students * per_student
            TutorFee.create_with_holiday(
                tutor_module=tutor_module,
                amount=amount,
                type_id=2,  # Teaching,  todo: use a choices object
                details='Extra students payment (%s)' % extra_students,
                approver=approver,
                hourly_rate=marking_hourly,
                weeks=1,
                raised_by=user.username
            )
