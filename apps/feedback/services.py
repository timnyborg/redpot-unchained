import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.feedback.models import Feedback
from apps.module.models import Module


def process_and_send_emails(module: Module) -> None:
    enrolments = (
        module.enrolments.filter(
            status__in=[10, 71, 90],
            qa__student__email__email__isnull=False,
            qa__student__email__is_default=True,
        )
        .select_related('module', 'qa', 'qa__student', 'qa__student__email')
        .values(
            'qa__student__id',
            'qa__student__firstname',
            'qa__student__surname',
            'id',
            'qa__student__email__email',
            'module',
            'module__id',
            'module__title',
            'module__code',
            'module__email',
            'module__portfolio__email',
        )
        .order_by(
            '-qa__student__email__email',
            'qa__student__surname',
            'qa__student__firstname',
        )
    )

    for enrolment in enrolments:
        email_context = {
            'firstname': enrolment['qa__student__firstname'],
            'email': enrolment['qa__student__email__email'],
            'module': enrolment['module'],
            'module_id': enrolment['module__id'],
            'module_title': enrolment['module__title'],
            'enrolment': enrolment['id'],
        }
        mod_contact = (
            enrolment['module__email'] if enrolment['module__email'] else enrolment['module__portfolio__email']
        )

        # Create object in table if object didn't exist
        student_feedback, created = Feedback.objects.get_or_create(enrolment=email_context['enrolment'], module=module)

        subject = f"Your feedback on {email_context['module_title']}"
        to = [settings.SUPPORT_EMAIL] if settings.DEBUG else [email_context['email']]
        if created:
            html_message = render_to_string('feedback/email/feedback_email.html', email_context)
            # todo: determine if it's worthwhile to bcc webmaster
            send_mail(subject, strip_tags(html_message), mod_contact, to, html_message=html_message)

            student_feedback.notified = datetime.datetime.now()
            student_feedback.save()

        elif not student_feedback.reminder:
            html_message = render_to_string('feedback/email/feedback_email_reminder.html', email_context)
            send_mail(subject, strip_tags(html_message), mod_contact, to, html_message=html_message)

            student_feedback.reminder = datetime.datetime.now()
            student_feedback.save()
