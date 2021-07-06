from __future__ import annotations

from typing import Union

from django.conf import settings
from django.core import mail
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.student.models import Address, Student

from .models import Tutor


# This method emails the personnel office when a change is detected in a tutor's name, address or bank details
def email_personnel_change(
    *,
    model: Union[Address, Student, Tutor],
    initial_values: dict,
    changed_data: list[str],
    request: HttpRequest,
    new_record: bool = False,
) -> bool:
    changes = []

    if not new_record:
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
            student = model.student
        elif isinstance(model, Address):
            fields = ['formatted']
            student = model.student
        elif isinstance(model, Student):
            fields = ['firstname', 'surname', 'title']
            student = model
        else:
            raise TypeError('Invalid type for argument `model`')

        # Build change log
        for field in changed_data:
            if field == 'formatted':
                # todo: addresses
                pass
                # changes.append('Address has changed from ' + (' '.join(format_address(old)) or '<blank>') + ' to '
                # + (' '.join(format_address(new)) or '<blank>'))
            elif field in fields:
                changes.append((field, initial_values[field], getattr(model, field)))

    elif isinstance(model, Address):
        # New address
        student = model.student
        # Todo: formatted address
        changes.append('New tutor address: ' + (' '.join(['FORMATTED ADDRESS']) or '<blank>'))
    else:
        # todo: description
        raise Exception()

    tutor = student.tutor
    # Send email(s) if any changes happened for a payroll/core tutor
    if not (tutor.employee_no and tutor.appointment_id and changes):
        # No email sent
        return False

    # Email personnel
    context = {
        'tutor': student,
        'updated_by': request.user.get_full_name(),
        'changes': changes,
        'canonical_url': settings.CANONICAL_URL,
    }
    message = render_to_string(
        request=request,
        template_name='email/personnel_info_change.html',
        context=context,
    )
    mail.send_mail(
        recipient_list=[settings.SUPPORT_EMAIL if settings.DEBUG else settings.PERSONNEL_EMAIL],
        from_email=settings.DEFAULT_FROM_EMAIL,
        subject='Tutor details update',
        message=strip_tags(message),
        html_message=message,
    )

    # Email tutor when account or sortcode changes
    tutor_email = student.emails.filter(is_default=True).first()
    if tutor_email and ('accountno' in changed_data or 'sortcode' in changed_data):
        message = render_to_string(
            request=request,
            template_name='email/tutor_info_change.html',
            context={'firstname': student.firstname, 'account': tutor.accountno[-3:], 'sortcode': tutor.sortcode[-2:]},
        )
        mail.send_mail(
            recipient_list=[settings.SUPPORT_EMAIL if settings.DEBUG else tutor_email],
            from_email=settings.DEFAULT_FROM_EMAIL,
            subject='Department for Continuing Education - payroll information',
            message=strip_tags(message),
            html_message=message,
        )

    # We've emailed personnel
    return True
