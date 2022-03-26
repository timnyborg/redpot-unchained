from datetime import datetime

from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.module.models import Module

SHORT_ONLINE_PORTFOLIO = 17


def render_reminder(*, module: Module, first_name: str) -> str:
    """Produce the email text; accessible from both the previewer and automated routine"""
    context = {
        'first_name': first_name,
        'module': module,
        'display_short_online_text': module.portfolio_id == SHORT_ONLINE_PORTFOLIO,
    }
    return render_to_string('reminder/email/message.html', context)


def mail_module_reminders(*, module: Module) -> int:
    enrolments = module.enrolments.filter(
        status__takes_place=True,  # confirmed variants and provisional
        qa__student__email__is_default=True,  # get default email addresses
    ).select_related('qa__student')

    students = [
        {
            'firstname': enrolment.qa.student.nickname or enrolment.qa.student.firstname,
            'email': enrolment.qa.student.get_default_email().email,
        }
        for enrolment in enrolments
    ]

    # Don't send from non-conted addresses (rare, but they can get confused and annoyed).
    # Plus, cross-domain stuff is spam-detector lightning
    from_email = module.email if '@conted' in module.email else 'enquiries@conted.ox.ac.uk'

    # Add the course admin as a recipient
    students.append({'firstname': 'Course admin', 'email': from_email})

    for student in students:
        message = render_reminder(module=module, first_name=student['firstname'])
        mail.send_mail(
            recipient_list=[settings.SUPPORT_EMAIL] if settings.HIJACK_ALL_EMAIL else [student['email']],
            from_email=from_email,
            subject=f'Course reminder: {module.title}',
            message=strip_tags(message),
            html_message=message,
            fail_silently=True,
        )

    module.reminder_sent_on = datetime.now()
    module.save()

    return len(enrolments)
