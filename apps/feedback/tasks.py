import datetime

from apps.feedback import services
from apps.module.models import Module
from redpot.celery import app


@app.task(name="feedback_mail_students")
def feedback_mail_students():
    yesterdays_finishers = datetime.date.today() - datetime.timedelta(days=1)
    week_old_reminders = datetime.date.today() - datetime.timedelta(days=6)

    # TODO: Consider allowing course admins an option to choose a different time delta for each module/portfolio?
    modules_for_feedback = Module.objects.filter(
        auto_feedback=True,
        is_cancelled=False,
        email__isnull=False,
        end_date__in=[yesterdays_finishers, week_old_reminders],
    )

    for module in modules_for_feedback:
        services.process_and_send_emails(module)

    return 'Success!'


@app.task(name="feedback_mail_dos_and_course_admin")
def feedback_mail_dos_and_course_admin():
    date = datetime.date.today() - datetime.timedelta(days=8)
    completed_modules = Module.objects.filter(
        auto_feedback=True, is_cancelled=False, email__isnull=False, end_date=date
    )

    for module in completed_modules:
        sent = services.mail_dos(module) if module.portfolio_id in [32, 31, 17] else None
        services.mail_course_admin(module, sent)

    return 'Success!'
