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
        models.PROTECT,
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
    www_buffer = models.IntegerField(default=0, help_text='Spaces that cannot be booked online')

    class Meta:
        db_table = 'limit'

    def __str__(self):
        return str(self.description)

    def get_absolute_url(self):
        return '#'

    def places_left(self, www_buffer: bool = True) -> int:
        return self.places - (self.www_buffer if www_buffer else 0) - self.bookings.count()
