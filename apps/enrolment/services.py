from __future__ import annotations

from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string

import apps.invoice.pdfs as invoice_pdfs
from apps.core.models import User
from apps.core.utils.dates import academic_year
from apps.invoice.models import Invoice
from apps.module.models import Module
from apps.qualification_aim.models import QualificationAim
from apps.student.models import Student
from apps.student.services import next_husid

from . import models


def create_enrolment(
    *, qa: QualificationAim, module: Module, status: models.EnrolmentStatus, user: User
) -> models.Enrolment:
    """Create an enrolment, while ensuring the student has a husid, qa.start_date is set, etc.
    This is a partial replacement of rp_api's create_enrolment, which has a lot of website-specific functionality
    (fees, overbooking emails, status setting, etc.)
    That functionality should be implemented in an RCP-accessible endpoint which in turn calls this function
    """

    # Create/Lookup HUSID number for student
    if not qa.student.husid:
        qa.student.husid = next_husid(academic_year=academic_year(module.start_date))
        qa.student.save()

    # If the QA doesn't have a start_date (COMDATE), or it's later than the module's, change it
    # todo: determine if qa.start_date has any value now that new hesa instances are generated annually
    if not qa.start_date or module.start_date and qa.start_date > module.start_date:
        qa.start_date = module.start_date
        qa.save()

    return models.Enrolment.objects.create(
        qa=qa,
        module=module,
        status=status,
        created_by=user.username,
        modified_by=user.username,
    )


def send_confirmation_email(
    *, student: Student, enrolments: list[models.Enrolment], invoices: list[Invoice], user: User
) -> None:
    """Sends a confirmation email to the admin, which they can amend and send to the student.  Attaches invoices"""
    context = {'enrolments': enrolments, 'invoices': invoices, 'student': student, 'sender': user}
    body = render_to_string('enrolment/email/confirmation.html', context=context)

    recipients = [settings.SUPPORT_EMAIL] if settings.HIJACK_ALL_EMAIL else [user.email]
    email = mail.EmailMessage(
        subject=f'Enrolment confirmation for {student}',
        body=body,
        to=recipients,
    )
    email.content_subtype = 'html'

    for invoice in invoices:
        content = invoice_pdfs.create_invoice(invoice)
        email.attach(filename=f'Invoice-{invoice}.pdf', content=content, mimetype='application/pdf')

    email.send()
