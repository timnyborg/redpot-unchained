from django.db import models
from django.urls import reverse

from apps.core.models import SignatureModel


class Accommodation(SignatureModel):
    class Types(models.IntegerChoices):
        SINGLE = (100, 'Single')
        TWIN = (200, 'Twin')
        __empty__ = ' - Select - '

    enrolment = models.ForeignKey(
        'enrolment.Enrolment', models.PROTECT, db_column='enrolment', related_name='accommodation'
    )
    type = models.IntegerField(choices=Types.choices)
    note = models.CharField(max_length=256, blank=True, null=True)
    limit = models.ForeignKey(
        'Limit',
        models.SET_NULL,
        db_column='limit',
        blank=True,
        null=True,
        related_name='bookings',
        related_query_name='booking',
    )

    class Meta:
        db_table = 'accommodation'

    def get_delete_url(self) -> str:
        return reverse('booking:delete-accommodation', kwargs={'pk': self.pk})


class Catering(SignatureModel):
    fee = models.ForeignKey('fee.Fee', models.PROTECT, db_column='fee', related_name='catering')
    enrolment = models.ForeignKey(
        'enrolment.Enrolment', models.PROTECT, db_column='enrolment', related_name='catering'
    )

    class Meta:
        db_table = 'catering'


class Limit(SignatureModel):
    """Accommodation limits that are shared between courses (e.g. spaces available to a week of summmer schools)"""

    description = models.CharField(max_length=128)
    places = models.IntegerField()
    online_booking_buffer = models.IntegerField(
        default=0, help_text='Spaces that cannot be booked online', db_column='www_buffer'
    )
    # todo: an is_active column, or a purge of old, unused records

    class Meta:
        db_table = 'limit'

    def __str__(self) -> str:
        return str(self.description)

    def get_absolute_url(self) -> str:
        # todo: consider separating details out from edit page
        return reverse('booking:edit-limit', kwargs={'pk': self.pk})

    def get_edit_url(self) -> str:
        return reverse('booking:edit-limit', kwargs={'pk': self.pk})

    def get_delete_url(self) -> str:
        return reverse('booking:delete-limit', kwargs={'pk': self.pk})

    def online_places_left(self) -> int:
        return self.paper_places_left() - self.online_booking_buffer

    def paper_places_left(self) -> int:
        return self.places - self.bookings.count()
