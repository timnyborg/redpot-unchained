from datetime import datetime, timedelta

from apps.core.utils.celery import mail_on_failure
from apps.module.models import Module
from redpot.celery import app

from . import services


@app.task(name='mail_reminders')
@mail_on_failure
def mail_reminders(*, days: int = 5) -> int:
    """Send out reminder emails for courses starting in 5 days' time"""
    modules = Module.objects.filter(
        auto_reminder=True,
        reminder_sent_on__isnull=True,
        is_cancelled=False,
        start_date=datetime.today() + timedelta(days=days),  # starting in 5 days
        # Validity checks
        email__isnull=False,
    )

    for module in modules:
        services.mail_module_reminders(module=module)

    return len(modules)
