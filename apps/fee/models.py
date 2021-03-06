from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from apps.core.models import SignatureModel


class FeeTypes(models.IntegerChoices):
    PROGRAMME = 7
    ACCOMMODATION = 3
    CATERING = 4
    COLLEGE = 11
    MISC = 2


class Fee(SignatureModel):
    module = models.ForeignKey('module.Module', models.PROTECT, db_column='module', related_name='fees')
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    type = models.ForeignKey(
        'FeeType',
        models.PROTECT,
        db_column='type',
        default=FeeTypes.PROGRAMME,
        limit_choices_to={'is_active': True},
    )
    description = models.CharField(max_length=64)
    eu_fee = models.BooleanField(
        db_column='eufee', default=False, verbose_name='Home/EU', help_text='Only payable by Home/EU students?'
    )
    is_visible = models.BooleanField(
        default=True, verbose_name='Visible', help_text='Make this fee visible on the website'
    )
    is_payable = models.BooleanField(
        default=True, verbose_name='Payable', help_text='Make this fee payable on the website'
    )
    is_catering = models.BooleanField(default=False, verbose_name='Catering', help_text='Includes catering')
    is_single_accom = models.BooleanField(
        default=False, verbose_name='Single accommodation', help_text='Includes a single accommodation'
    )
    is_twin_accom = models.BooleanField(
        default=False, verbose_name='Double accommodation', help_text='Includes a double accommodation'
    )
    credit_fee = models.BooleanField(default=False, help_text='Additional fee to take the class for credit')
    end_date = models.DateField(
        blank=True, null=True, help_text='Optional: day on which to remove the fee from the website'
    )
    limit = models.ForeignKey(
        to='booking.Limit',
        on_delete=models.SET_NULL,
        related_name='fees',
        related_query_name='fee',
        blank=True,
        null=True,
        db_column='limit',
    )
    allocation = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Catering allocation',
        help_text='Optional: maximum purchasable on the website',
    )

    catering_bookings = models.ManyToManyField(
        'enrolment.Enrolment',
        through='booking.Catering',
    )

    def catering_booking_count(self):
        return self.catering_bookings.filter(status__takes_place=True).count()

    class Meta:
        db_table = 'fee'

    def __str__(self):
        return str(self.description)

    def get_absolute_url(self):
        return reverse('fee:edit', args=[self.pk])

    def get_delete_url(self):
        return reverse('fee:delete', args=[self.pk])

    def clean(self):
        # Catering fees should always have their flag set (common user-error)
        if self.type_id == FeeTypes.CATERING:
            self.is_catering = True

        # Limit should only be set if an accommodation flag is true
        if self.limit and not (self.is_single_accom or self.is_twin_accom):
            raise ValidationError({'limit': 'The fee must be marked as a single or twin accommodation to use a limit'})

    @property
    def finance_code(self) -> str:
        """Generate a finance code from the parent module's finance code and the account"""
        parent = self.module
        if not parent.finance_code:
            return ''
        return f'{parent.cost_centre} {self.type.account_id} {parent.activity_code} {parent.source_of_funds}'


class FeeType(models.Model):
    narrative = models.CharField(max_length=64, blank=True, null=True)
    account = models.ForeignKey('finance.Account', models.PROTECT, db_column='account')
    display_order = models.IntegerField(blank=True, null=True)
    is_tuition = models.BooleanField()
    is_active = models.IntegerField()

    class Meta:
        db_table = 'fee_type'
        ordering = ('display_order',)

    def __str__(self):
        return f'{self.narrative}'
