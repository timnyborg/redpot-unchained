from datetime import date, datetime

from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

from apps.core.models import AddressModel, SignatureModel
from apps.core.utils.models import PhoneField

CUSTOM_PLAN_TYPE = 16
CUSTOM_PAYMENT_PENDING_STATUS = 2


class InvoiceQuerySet(models.QuerySet):
    def outstanding(self):
        # Subquery - get a list of invoices with ledger totals > 0
        # The performance may get worse as the number of invoices increases, in which case, it may be faster if the
        #   subquery uses an outer reference, rather than being a big 'IN' check
        outstanding = models.Subquery(
            Invoice.objects.annotate(balance=models.Sum('allocated_ledger_items__amount'))
            .filter(balance__gt=0)
            .values('id')
        )

        # Apply a filter to the queryset, limiting it to those outstanding invoices, plus check they're overdue
        return self.filter(id__in=outstanding)

    def overdue(self):
        # Overdue only applies to outstanding
        return self.outstanding().filter(due_date__lt=date.today())


class Invoice(AddressModel, SignatureModel):
    number = models.IntegerField(unique=True, editable=False)
    prefix = models.CharField(max_length=32, default='XG', editable=False)
    date = models.DateField(default=datetime.now)
    due_date = models.DateField(null=True, db_column='duedate')
    fao = models.CharField(max_length=128, blank=True, null=True, verbose_name='FAO')
    invoiced_to = models.CharField(max_length=128, verbose_name='Invoice to')

    amount = models.DecimalField(max_digits=19, decimal_places=4, editable=False)
    custom_narrative = models.BooleanField(default=False)
    narrative = models.TextField(blank=True, null=True)
    ref_no = models.CharField(max_length=64, blank=True, null=True, verbose_name='Customer ref. #')
    contact_person = models.CharField(max_length=128)
    contact_email = models.EmailField(max_length=255)
    contact_phone = PhoneField(max_length=64)
    vat_no = models.CharField(max_length=64, blank=True, null=True, verbose_name='VAT #')

    ledger_items = models.ManyToManyField(
        'finance.Ledger', through='InvoiceLedger', through_fields=('invoice', 'ledger')
    )

    # Artificial many-to-many to support our obsolete credit note allocation nonsense
    allocated_ledger_items = models.ManyToManyField(
        'finance.Ledger',
        through='InvoiceLedger',
        through_fields=('allocation', 'ledger'),
        related_name='allocated_invoice',
    )

    objects = InvoiceQuerySet.as_manager()

    class Meta:
        db_table = 'invoice'

    def __str__(self):
        return f'{self.prefix}{self.number}'

    def get_absolute_url(self):
        return reverse('invoice:view', args=[self.id])

    def get_edit_url(self):
        return reverse('invoice:edit', args=[self.id])

    @cached_property
    def balance(self):
        return self.allocated_ledger_items.aggregate(sum=models.Sum('amount'))['sum']

    def get_fees(self):
        """Quickly get all an invoice's fee lines.  Fees are add with an incrementing `number`"""
        return self.ledger_items.filter(invoice_ledger__item_no__gt=0)

    def get_payments(self):
        """Quickly get all an invoice's payment lines.  Payments are added with `number`=0"""
        return self.ledger_items.filter(invoice_ledger__item_no=0)

    def get_credit_note_items(self):
        """Get items on (legacy) credit notes, which are attached to a separate invoice but allocated to this one"""
        return self.allocated_ledger_items.exclude(invoice=self.pk)

    def written_off(self) -> bool:
        return self.allocated_ledger_items.non_cash().total() == 0


class InvoiceLedger(models.Model):
    ledger = models.OneToOneField(
        'finance.Ledger', models.DO_NOTHING, db_column='ledger', related_name='invoice_ledger'
    )
    invoice = models.ForeignKey(Invoice, models.DO_NOTHING, db_column='invoice', related_name='invoice_ledger')
    # Awful backwards-compatibility. Allocation was used some items on some invoices ("credit notes") paid off others?!
    # Todo: change the foreign key to point to id rather than number, to be consistent with `invoice`
    allocation = models.ForeignKey(
        Invoice,
        models.DO_NOTHING,
        db_column='allocation',
        to_field='number',
        related_name='invoice_ledger_allocations',
    )
    # todo: replace this with a useful type field: something like FEE/CREDIT/PAYMENT, or ATTACHED/NONATTACHED.
    #       The numbering is useless, since you can just order by ledger date and pk
    item_no = models.IntegerField()  # fees at the time of invoicing are given values 1, 2, 3...  Payments are given 0

    class Meta:
        db_table = 'invoice_ledger'


class PaymentPlan(SignatureModel):
    # Constants used in logic - todo: move to enums
    CUSTOM_TYPE = 16
    PENDING_STATUS = 1  # student has selected a plan, but not activated it
    CUSTOM_PENDING_STATUS = 2  # staff have configured a plan, but not activated it

    type = models.ForeignKey('PaymentPlanType', models.DO_NOTHING, db_column='type')
    status = models.ForeignKey('PaymentPlanStatus', models.DO_NOTHING, db_column='status')
    # This hasn't strictly been a 1-to-1 relationship, but we've treated it as one for years
    invoice = models.OneToOneField(
        'Invoice',
        models.DO_NOTHING,
        related_name='payment_plan',
        db_column='invoice',
    )
    amount = models.DecimalField(max_digits=19, decimal_places=4)

    class Meta:
        db_table = 'payment_plan'

    def is_pending_activation(self):
        return self.status_id == self.PENDING_STATUS

    def is_custom(self):
        return self.type_id == self.CUSTOM_TYPE


class ScheduledPayment(SignatureModel):
    payment_plan = models.ForeignKey(
        PaymentPlan,
        models.DO_NOTHING,
        db_column='payment_plan',
        related_name='scheduled_payments',
        related_query_name='scheduled_payment',
    )
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    is_deposit = models.BooleanField()  # todo: investigate if this has value

    class Meta:
        db_table = 'payment_plan_schedule'
        ordering = ('due_date',)


# Todo: consider whether to remove and convert status to a text field with choices
class PaymentPlanStatus(models.Model):
    description = models.CharField(max_length=64)

    class Meta:
        db_table = 'payment_plan_status'

    def __str__(self):
        return self.description


class PaymentPlanType(SignatureModel):
    class FrequencyChoices(models.TextChoices):
        IMMEDIATELY = "IMMEDIATELY", "Immediately"
        TERMLY = "TERMLY", "Termly"
        MONTHLY = "MONTHLY", "Monthly"

    name = models.CharField(max_length=128)
    deposit = models.DecimalField(max_digits=16, decimal_places=2)
    payments = models.IntegerField(blank=True, null=True)
    payments_due = models.CharField(max_length=32, blank=True, null=True, choices=FrequencyChoices.choices)
    start_month = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'payment_plan_type'
        ordering = ('payments_due', 'deposit', 'payments')

    def __str__(self):
        return self.name


class ModulePaymentPlan(models.Model):
    module = models.ForeignKey('module.Module', models.DO_NOTHING, db_column='module')
    plan_type = models.ForeignKey('PaymentPlanType', models.DO_NOTHING, db_column='plan_type')

    class Meta:
        db_table = 'module_payment_plan'
