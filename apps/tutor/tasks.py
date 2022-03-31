from datetime import datetime

from dateutil.relativedelta import relativedelta

from django.db.models import DateTimeField, Max, Q
from django.db.models.functions import Coalesce

from apps.core.utils.celery import mail_on_failure
from redpot.celery import app

from . import models


@app.task(name='remove_old_banking_details')
@mail_on_failure
def remove_old_banking_details(*, years=6, months=0) -> int:
    """Wipe the banking/NI details of all tutors who
    - Have banking or NINO details
    - Have no courses that ended in the last 6 years
         (falling back on start or created date where modules have no end dates)
    - Tutor record not updated in last 12 months
    todo: could be a lot simpler by relying on tutor payments instead, if personnel approves
    """

    empty_fields = {
        'bankname': '',
        'accountname': '',
        'accountno': '',
        'branchaddress': '',
        'nino': '',
        'iban': '',
        'sortcode': '',
        'swift': '',
        'other_bank_details': '',
    }

    updated = (
        models.Tutor.objects.filter(
            modified_on__lt=datetime.now() - relativedelta(years=1),
        )
        .exclude(**empty_fields)  # Exclude anyone without nullable data
        .annotate(
            latest_end=Max(
                Coalesce(
                    'modules__end_date',
                    'modules__start_date',
                    'modules__created_on',
                    output_field=DateTimeField(),
                )
            ),
        )
        .filter(
            Q(latest_end__lt=datetime.now() - relativedelta(years=years, months=months)) | Q(latest_end__isnull=True)
        )
        .update(**empty_fields)
    )

    return updated
