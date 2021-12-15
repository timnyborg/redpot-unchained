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
