from datetime import datetime

from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils import html

from apps.contract import models
from apps.contract.models import Statuses
from apps.core.models import User
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


def approve_contracts(*, contract_ids: list, user: User) -> int:
    """Approves contracts assigned to a user"""
    contracts = user.approver_contracts.filter(status=Statuses.AWAITING_APPROVAL, id__in=contract_ids)
    return contracts.update(
        status=Statuses.APPROVED_AWAITING_SIGNATURE,
        approved_by=user.username,
        approved_on=datetime.now(),
    )


def sign_contracts(*, contract_ids: list, user: User) -> int:
    """Signs contracts and sends out notification emails"""
    contracts = models.Contract.objects.filter(status=Statuses.APPROVED_AWAITING_SIGNATURE, id__in=contract_ids)
    for contract in contracts:
        send_notification_mail(contract=contract)
    return contracts.update(
        status=Statuses.SIGNED_BY_DEPARTMENT,
        signed_by=user.username,
        signed_on=datetime.now(),
    )


def mail_pending_contracts_signature() -> int:
    """Email reminder to sign pending contracts"""
    outstanding = models.Contract.objects.filter(status=Statuses.APPROVED_AWAITING_SIGNATURE).count()

    if outstanding:
        context = {
            'outstanding': outstanding,
            'name': 'Sean Faughnan',
            'email': 'personnel@conted.ox.ac.uk',
            'url': settings.CANONICAL_URL + '/contract/need-signature',
        }
        message = render_to_string('contract/email/pending_tutor_contracts_signatures.html', context=context)

        recipients = [settings.SUPPORT_EMAIL] if settings.DEBUG else settings.CONTRACT_SIGNATURE_EMAILS
        mail.send_mail(
            recipient_list=recipients,
            from_email=settings.DEFAULT_FROM_EMAIL,
            subject='Tutor contracts awaiting signature',
            message=html.strip_tags(message),
            html_message=message,
        )

    return outstanding
