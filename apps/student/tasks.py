from datetime import datetime

from dateutil.relativedelta import relativedelta

from apps.core.utils.celery import mail_on_failure
from redpot.celery import app

from . import models


@app.task(name='update_formatted_addresses')
@mail_on_failure
def update_formatted_addresses() -> int:
    """Scheduled routine to update the formatted field in addresses after the SITS daily load"""
    # todo: determine if the `formatted` column still serves a purpose (SSRS reporting?) and remove if not.
    unformatted_addresses = models.Address.objects.filter(formatted__isnull=True, line1__isnull=False)
    # Setting `formatted` is done in def save(), so we can just re-save the objects
    for address in unformatted_addresses:
        address.save()
    return len(unformatted_addresses)


@app.task(name='remove_old_enquiries')
@mail_on_failure
def remove_old_enquiries(*, years=3, months=0) -> int:
    """Simply identify all enquiry records created before a given date and delete them.
    Returns a row count"""
    deleted, _ = models.Enquiry.objects.filter(
        created_on__lt=datetime.now() - relativedelta(years=years, months=months)
    ).delete()
    return deleted
