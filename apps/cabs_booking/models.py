from django.db import models

from apps.core.models import SignatureModel


class CABSBooking(SignatureModel):
    """Records the result of booking a module's dates on CABS"""

    module = models.ForeignKey(
        'module.Module',
        models.CASCADE,
        db_column='module',
        related_name='cabs_bookings',
        related_query_name='cabs_booking',
    )
    mbr_id = models.CharField(max_length=16)
    confirmed = models.IntegerField(null=True)  # A count of confirmed-status bookings
    provisional = models.IntegerField(null=True)  # A count of provisional-status bookings

    class Meta:
        db_table = 'module_cabs_booking'
