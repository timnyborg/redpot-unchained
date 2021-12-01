from __future__ import annotations

from datetime import datetime, timedelta
from typing import Union

from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.core.models import User
from apps.student.models import Address, Student

from .models import Tutor


def _notifiable(tutor: Tutor) -> bool:
    """Send email(s) only regarding payroll/core tutors, ignoring those created in the last day"""
    return bool(tutor.created_on < datetime.now() - timedelta(days=1) and tutor.employee_no and tutor.appointment_id)


def email_personnel_change(
    *,
    model: Union[Address, Student, Tutor],
    initial_values: dict,
    changed_data: list[str],
    user: User,
) -> bool:
    """Emails the personnel office when a change is detected in a tutor's name, address or bank details"""
    # Discern update source
    if isinstance(model, Tutor):
        fields = [
            'bankname',
            'branchaddress',
            'accountname',
            'sortcode',
            'accountno',
            'swift',
            'iban',
            'other_bank_details',
        ]
        tutor = model
    elif isinstance(model, Address):
        fields = ['line1', 'line2', 'line3', 'town', 'state', 'country', 'postcode']
        tutor = model.student.tutor
    elif isinstance(model, Student):
        fields = ['firstname', 'surname', 'title']
        tutor = model.tutor
    else:
        raise TypeError('Invalid type for argument `model`')

    # Build change log
    changes = [(f, initial_values.get(f), getattr(model, f)) for f in fields if f in changed_data]

    if not changes or not _notifiable(tutor):
        # No email sent
        return False

    # Email personnel
    context = {
        'person': tutor.student,
        'updated_by': user.get_full_name(),
        'changes': changes,
        'canonical_url': settings.CANONICAL_URL,
    }
    message = render_to_string(template_name='email/personnel_info_change.html', context=context)
    mail.send_mail(
        recipient_list=[settings.SUPPORT_EMAIL if settings.DEBUG else settings.PERSONNEL_EMAIL],
        from_email=settings.DEFAULT_FROM_EMAIL,
        subject='Tutor details update',
        message=strip_tags(message),
        html_message=message,
    )

    # Email tutor when account or sortcode changes
    tutor_email = tutor.student.get_default_email()
    if tutor_email and ('accountno' in changed_data or 'sortcode' in changed_data):
        context = {
            'firstname': tutor.student.firstname,
            'account': tutor.accountno,
            'sortcode': tutor.sortcode,
        }
        message = render_to_string(template_name='email/tutor_info_change.html', context=context)
        mail.send_mail(
            recipient_list=[settings.SUPPORT_EMAIL if settings.DEBUG else tutor_email],
            from_email=settings.DEFAULT_FROM_EMAIL,
            subject='Department for Continuing Education - payroll information',
            message=strip_tags(message),
            html_message=message,
        )
    return True
