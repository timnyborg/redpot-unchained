from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from django.db import models
from django.urls import reverse

from apps.core.models import SignatureModel

DEBTOR_ACCOUNT = 'Z300'


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


class Invoice(SignatureModel):
    number = models.IntegerField(unique=True, editable=False)
    prefix = models.CharField(max_length=32, default='XG', editable=False)
    date = models.DateField(default=datetime.now)
    due_date = models.DateField(null=True, db_column='duedate')
    fao = models.CharField(max_length=128, blank=True, null=True, verbose_name='FAO')
    invoiced_to = models.CharField(max_length=128, verbose_name='Invoice to')
    line1 = models.CharField(max_length=128, blank=True, null=True, verbose_name='Address line 1')
    line2 = models.CharField(max_length=128, blank=True, null=True, verbose_name='Line 2')
    line3 = models.CharField(max_length=128, blank=True, null=True, verbose_name='Line 3')
    town = models.CharField(max_length=64, blank=True, null=True, verbose_name='City/town')
    countystate = models.CharField(max_length=64, blank=True, null=True, verbose_name='County/state')
    country = models.CharField(max_length=64, blank=True, null=True)
    postcode = models.CharField(max_length=32, blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4, editable=False)
    custom_narrative = models.BooleanField(default=False)
    narrative = models.TextField(blank=True, null=True)
    ref_no = models.CharField(max_length=64, blank=True, null=True, verbose_name='Customer ref. #')
    division = models.IntegerField(blank=True, null=True, editable=False)
    contact_person = models.CharField(max_length=128, blank=True, null=True)
    contact_email = models.CharField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=64, blank=True, null=True)
    company = models.CharField(max_length=128, blank=True, null=True)
    formatted_addressee = models.TextField(blank=True, null=True)
    vat_no = models.CharField(max_length=64, blank=True, null=True, verbose_name='VAT #')

    ledger_items = models.ManyToManyField('Ledger', through='InvoiceLedger', through_fields=('invoice', 'ledger'))

    # Artificial many-to-many to support our obsolete credit note allocation nonsense
    allocated_ledger_items = models.ManyToManyField(
        'Ledger', through='InvoiceLedger', through_fields=('allocation', 'ledger'), related_name='allocated_invoice'
    )

    objects = InvoiceQuerySet.as_manager()

    class Meta:
        # managed = False
        db_table = 'invoice'

    def __str__(self):
        return f'{self.prefix}{self.number}'

    def get_absolute_url(self):
        return reverse('invoice:view', args=[self.id])

    def get_edit_url(self):
        return reverse('invoice:edit', args=[self.id])

    def balance(self):
        return self.allocated_ledger_items.aggregate(sum=models.Sum('amount'))['sum']

    def get_fees(self):
        # Quickly get all an invoice's fee lines.  Fees are add with an incrementing `number`
        return self.ledger_items.filter(invoice_ledger__item_no__gt=0)

    def get_payments(self):
        # Quickly get all an invoice's payment lines.  Payments are added with `number`=0
        return self.ledger_items.filter(invoice_ledger__item_no=0)


class InvoiceLedger(models.Model):
    ledger = models.ForeignKey('Ledger', models.DO_NOTHING, db_column='ledger', related_name='invoice_ledger')
    invoice = models.ForeignKey(Invoice, models.DO_NOTHING, db_column='invoice', related_name='invoice_ledger')
    # Awful backwards-compatibility. Allocation was used some items on some invoices ("credit notes") paid off others?!
    allocation = models.ForeignKey(
        Invoice,
        models.DO_NOTHING,
        db_column='allocation',
        to_field='number',
        related_name='invoice_ledger_allocations',
    )
    item_no = models.IntegerField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'invoice_ledger'


class TransactionType(models.Model):
    description = models.CharField(max_length=32, blank=True, null=True)
    is_cash = models.BooleanField()
    is_active = models.BooleanField(default=True)

    class Meta:
        # managed = False
        db_table = 'transaction_type'

    def __str__(self):
        return self.description


class LedgerQuerySet(models.QuerySet):
    def debts(self) -> models.QuerySet:
        return self.filter(account=DEBTOR_ACCOUNT)

    def invoiced(self) -> models.QuerySet:
        return self.filter(invoice_ledger__id__isnull=False)

    def uninvoiced(self) -> models.QuerySet:
        return self.filter(invoice_ledger__id__isnull=True)

    def balance(self) -> Optional[Decimal]:
        """Convenience function to get the sum of the queryset"""
        # todo: should the `or Decimal(0)` go in here, making it non optional?
        return self.aggregate(balance=models.Sum('amount'))['balance']


# ledger should got in a finance models file (or core model file)
class Ledger(models.Model):
    date = models.DateTimeField()
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    finance_code = models.CharField(max_length=64, blank=True, null=True)
    narrative = models.CharField(max_length=128)
    # todo: investigate if this (division) has value
    division = models.ForeignKey('core.Division', models.DO_NOTHING, db_column='division', blank=True, null=True)
    type = models.ForeignKey('TransactionType', models.DO_NOTHING, db_column='type')
    # account = models.ForeignKey('LedgerAccount', models.DO_NOTHING, db_column='account', blank=True, null=True)
    account = models.CharField(max_length=4, db_column='account')
    enrolment = models.ForeignKey(
        'enrolment.Enrolment', models.DO_NOTHING, db_column='enrolment', blank=True, null=True
    )

    allocation = models.IntegerField()
    ref_no = models.IntegerField(blank=True, null=True)
    batch = models.IntegerField(blank=True, null=True)

    objects = LedgerQuerySet.as_manager()

    class Meta:
        # managed = False
        db_table = 'ledger'


class PaymentPlan(SignatureModel):
    # Constants used in logic (because we are using foreign keys, not choices)
    CUSTOM_TYPE = 16
    PENDING_STATUS = 1  # student has selected a plan, but not activated it

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
        # managed = False
        db_table = 'payment_plan'

    def is_pending_activation(self):
        return self.status_id == self.PENDING_STATUS

    def is_custom(self):
        return self.type_id == self.CUSTOM_TYPE


class PaymentPlanSchedule(SignatureModel):
    CUSTOM_TYPE = 16

    payment_plan = models.ForeignKey(PaymentPlan, models.DO_NOTHING, db_column='payment_plan', related_name='schedule')
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    number = models.IntegerField()  # todo: investigate if this has value
    is_deposit = models.BooleanField()  # todo: investigate if this has value

    class Meta:
        # managed = False
        db_table = 'payment_plan_schedule'


# Todo: consider whether to remove and convert status to a text field with choices
class PaymentPlanStatus(models.Model):
    description = models.CharField(max_length=64)

    class Meta:
        # managed = False
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
        # managed = False
        db_table = 'payment_plan_type'

    def __str__(self):
        return self.name


class ModulePaymentPlan(models.Model):
    module = models.ForeignKey('module.Module', models.DO_NOTHING, db_column='module')
    plan_type = models.ForeignKey('PaymentPlanType', models.DO_NOTHING, db_column='plan_type')

    # Obsolete
    # deposit = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'module_payment_plan'
