from django.conf import settings
from django.core import mail
from django.db.models import Count
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.core.models import User
from apps.core.utils.celery import mail_on_failure
from redpot.celery import app

from . import models


@app.task(name="mail_pending_tutor_payments")
@mail_on_failure
def mail_pending_tutor_payments() -> int:
    approvers_with_payments = (
        User.objects.filter(approver_payment__status=models.Statuses.RAISED)
        .exclude(email='')
        .annotate(payments=Count('approver_payment'))
    )

    for user in approvers_with_payments:
        message = render_to_string(
            'tutor_payment/email/pending_tutor_payments.html',
            context={'payments': user.payments, 'first_name': user.first_name, 'redpot_url': settings.CANONICAL_URL},
        )
        mail.send_mail(
            subject='Tutor payments awaiting your approval',
            recipient_list=[settings.SUPPORT_EMAIL] if settings.HIJACK_ALL_EMAIL else [user.email],
            message=strip_tags(message),
            html_message=message,
            from_email=None,
        )

    return len(approvers_with_payments)
