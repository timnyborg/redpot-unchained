import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.enrolment.models import Enrolment
from apps.feedback.models import Feedback
from apps.module.models import Module


def process_and_send_emails(module):
    enrolments = (
        Enrolment.objects.filter(
            module=module,
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

    email_context = {}
    for student in enrolments:
        email_context['firstname'] = student['qa__student__firstname']
        email_context['email'] = student['qa__student__email__email']
        email_context['module'] = student['module']
        email_context['module_id'] = student['module__id']
        email_context['module_title'] = student['module__title']
        email_context['enrolment'] = student['id']
        mod_contact = student['module__email'] if student['module__email'] else student['module__portfolio__email']

        student_feedback = Feedback.objects.filter(enrolment=email_context['enrolment'])

        if not student_feedback:
            subject = 'Your feedback on ' + email_context['module_title']
            html_message = render_to_string('feedback/email/feedback_email.html', email_context)
            plain_message = strip_tags(html_message)
            from_email = mod_contact
            # todo: determine if it's worthwhile to bcc webmaster
            to = [settings.SUPPORT_EMAIL] if settings.DEBUG else [email_context['email']]
            send_mail(subject, plain_message, from_email, to, html_message=html_message)

            # Create object in table if object didn't exist
            Feedback.objects.create(
                module=Module.objects.get(id=email_context['module_id']),
                enrolment=email_context['enrolment'],
                notified=datetime.datetime.now(),
            )

        elif not student_feedback.first().reminder:
            subject = 'Your feedback on ' + email_context['module_title']
            html_message = render_to_string('feedback/email/feedback_email_reminder.html', email_context)
            plain_message = strip_tags(html_message)
            from_email = mod_contact
            to = [settings.SUPPORT_EMAIL] if settings.DEBUG else [email_context['email']]
            send_mail(subject, plain_message, from_email, to, html_message=html_message)
            Feedback.objects.filter(enrolment=email_context['enrolment']).update(reminder=datetime.datetime.now())
