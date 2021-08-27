from __future__ import annotations

import re
from datetime import datetime

from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import apps.finance.services as finance_services
from apps.core.models import User
from apps.finance.models import Accounts, Ledger, TransactionTypes
from apps.invoice.models import Invoice
from apps.module.models import Module

from . import models


def get_narrative(*, amendment: models.Amendment) -> str:
    """Populate default value for narrative field"""
    narrative_strings: dict[int:str] = {
        models.AmendmentTypes.AMENDMENT: 'INF {amendment.id} - Write off - {amendment.reason}',
        models.AmendmentTypes.CREDIT_CARD_REFUND: 'REF {amendment.id} - Refund (cc) - {amendment.reason}',
        models.AmendmentTypes.OTHER_REFUND: 'REF {amendment.id} - Refund (paper form) - {amendment.reason}',
        models.AmendmentTypes.BANK_REFUND: 'REF {amendment.id} - Refund (bank return) - {amendment.reason}',
    }
    if amendment.type_id in narrative_strings:
        return narrative_strings[amendment.type_id].format(amendment=amendment)

    # Todo: this method is a piece of work, and needs rethinking.  Replace with strategy pattern?
    if amendment.type_id == models.AmendmentTypes.TRANSFER:  # Transfer
        if amendment.transfer_module:  # to another course
            if amendment.transfer_module == 'multiple':
                transfer_module = 'multiple'
            else:
                module = Module.objects.get(pk=amendment.transfer_module)
                transfer_module = module.code
            code = amendment.enrolment.module.code
            narrative = f'INF {amendment.id} - Transfer from {code} to {transfer_module}'

        elif amendment.transfer_enrolment:  # to another student
            from_student = amendment.enrolment.qa.student
            to_student = amendment.transfer_enrolment.qa.student
            to_module = amendment.transfer_enrolment.module
            narrative = f'INF {amendment.id} - Transfer from {from_student} to {to_student} on {to_module.code}'
        elif amendment.transfer_invoice:  # to another invoice
            # todo: fix this horrible bit of double-table foreign-keying!  Should only point to invoice
            invoice = Invoice.objects.filter(pk=amendment.source_invoice).first()
            if invoice:
                source = f'invoice {invoice}'
            else:
                ledger = Ledger.objects.get(pk=amendment.source_invoice)
                source = f'payment {ledger.narrative}'
            narrative = f'INF {amendment.id} - Transfer from {source} to {amendment.transfer_invoice}'
        else:
            raise Exception('Amendment lacks an enrolment, student, or invoice to transfer to')

    elif amendment.type_id == models.AmendmentTypes.ONLINE_REFUND:
        narrative = f'REF {amendment.id} - Refund - {amendment.reason}'
        # todo: investigate the point of this
        ledger_narratives = (
            amendment.enrolment.ledger_set.debts()
            .filter(amount__lt=0, type=TransactionTypes.ONLINE, narrative__like='%contCPG%')
            .values_list('narrative', flat=True)
        )
        if len(ledger_narratives) == 1:  # Only if there's only one
            online_payment = re.findall(r'contCPG\d*', ledger_narratives[0])[0]
            narrative += f' - {online_payment}'
    elif amendment.type_id == models.AmendmentTypes.RCP_REFUND:
        narrative = f'REF {amendment.id} - Refund (rcp) - {amendment.reason}'
        # todo: investigate the point of this
        ledger = amendment.enrolment.ledger_set.debts().filter(amount__lt=0, type=TransactionTypes.RCP).first()
        if ledger:
            narrative += f" - …{ledger.narrative[-80:-10]}"
    else:
        raise Exception(f'Invalid amendment type: {amendment.type}')

    return narrative


def user_can_edit(*, user: User, amendment: models.Amendment) -> bool:
    """Determine if a user can edit (or delete) an amendment, given their rights and its status"""
    return (
        user.has_perm('amendment.edit_finance')
        or user.has_perm('amendment.approve')
        and user.username == amendment.approver
        and amendment.status_id in (models.AmendmentStatuses.RAISED, models.AmendmentStatuses.APPROVED)
        or user.username == amendment.requested_by
        and amendment.status_id == models.AmendmentStatuses.RAISED
    )


def approve_amendments(*, amendment_ids: list[int], username: str) -> int:
    """Approve a set of amendments, provided their approver matches the provided username"""
    amendments = models.Amendment.objects.filter(
        status_id=models.AmendmentStatuses.RAISED,
        approver=username,
        id__in=amendment_ids,
    )
    for amendment in amendments:
        send_request_approved_email(amendment=amendment)
    return amendments.update(
        status=models.AmendmentStatuses.APPROVED, approved_by=username, approved_on=datetime.now()
    )


def send_request_created_email(*, amendment: models.Amendment) -> None:
    """Email the approver when a change request is raised"""
    assert amendment.approver is not None, 'Approver is not set'  # todo: remove once approver is notnull
    recipient: str = amendment.approver.email
    context = {
        'student': amendment.enrolment.qa.student,
        'module': amendment.enrolment.module,
        'canonical_url': settings.CANONICAL_URL,
    }
    message = render_to_string('email/change_request_created.html', context=context)
    mail.send_mail(
        recipient_list=[settings.SUPPORT_EMAIL if settings.DEBUG else recipient],
        from_email=settings.SUPPORT_EMAIL,
        subject=f'Finance change request from {amendment.requested_by} awaits your approval',
        message=strip_tags(message),
        html_message=message,
    )


def send_request_approved_email(*, amendment: models.Amendment) -> None:
    """Email the requester when a change request is approved"""
    recipient: str = amendment.requested_by.email
    context = {
        'student': amendment.enrolment.qa.student,
        'module': amendment.enrolment.module,
    }
    message = render_to_string('email/change_request_approved.html', context=context)
    mail.send_mail(
        recipient_list=[settings.SUPPORT_EMAIL if settings.DEBUG else recipient],
        from_email=settings.SUPPORT_EMAIL,
        subject='Finance change request approved and sent for execution',
        message=strip_tags(message),
        html_message=message,
    )


def send_request_complete_email(*, amendment: models.Amendment) -> None:
    """Email the requester when a change request is completed"""
    recipient: str = amendment.requested_by.email
    context = {
        'student': amendment.enrolment.qa.student,
        'module': amendment.enrolment.module,
    }
    message = render_to_string('email/change_request_complete.html', context=context)
    mail.send_mail(
        recipient_list=[settings.SUPPORT_EMAIL if settings.DEBUG else recipient],
        from_email=settings.SUPPORT_EMAIL,
        subject='Finance change request completed successfully',
        message=strip_tags(message),
        html_message=message,
    )


def apply_online_refund(*, amendment: models.Amendment, user: User) -> None:
    """Automatically creates fee lines for an online refund"""
    # Subtract cash
    finance_services.insert_ledger(
        account_code=Accounts.CASH,
        finance_code=amendment.enrolment.module.finance_code,
        narrative=amendment.narrative,
        amount=amendment.amount,
        type_id=TransactionTypes.ONLINE,
        enrolment_id=amendment.enrolment.id,
        user=user,
    )
    # Writeoff fee
    finance_services.insert_ledger(
        account_code=Accounts.TUITION,
        finance_code=amendment.enrolment.module.finance_code,
        narrative=amendment.narrative,
        amount=-amendment.amount,
        type_id=TransactionTypes.WRITEOFF,
        enrolment_id=amendment.enrolment.id,
        user=user,
    )
