from datetime import datetime

from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils import html

from apps.contract import models
from apps.core.utils.postal import FormattedAddress
from apps.tutor.models import RightToWorkType


def generate_fixed_properties(*, contract: models.Contract) -> dict:
    """Produces a set of fixed contract attributes, which won't change if related models are edited
    Could be part of Contract.save()
    """
    tutor = contract.tutor_module.tutor
    student = tutor.student
    module = contract.tutor_module.module
    address = student.get_default_address()
    return {
        'full_name': f"{student.title or ''} {student.firstname} {student.surname}",
        'salutation': f"{student.title or student.firstname} {student.surname}",
        'doc_date': datetime.today(),
        'address': FormattedAddress(address).as_list(),
        'module': {'title': module.title, 'code': module.code},
        'list_a_rtw': tutor.rtw_type == RightToWorkType.PERMANENT,
        'overseas_rtw': tutor.rtw_type == RightToWorkType.OVERSEAS,
    }


def send_notification_mail(*, contract: models.Contract) -> int:
    """Email the contract's notification address (when it is signed).  Returns True if an email was sent"""
    if not contract.email_notification:
        return 0
    context = {
        'tutor_name': contract.options['full_name'],
        'module_name': contract.tutor_module.module.title,
        'module_code': contract.tutor_module.module.code,
        'url': settings.CANONICAL_URL + contract.get_absolute_url(),
    }
    message = render_to_string('contract/email/signed_notification.html', context=context)
    recipients = [settings.SUPPORT_EMAIL if settings.DEBUG else contract.email_notification]
    return mail.send_mail(
        subject='Contract - signed',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        message=html.strip_tags(message),
        html_message=message,
    )
