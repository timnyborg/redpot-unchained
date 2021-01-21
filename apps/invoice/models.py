from django.db import models
from django.urls import reverse
from apps.main.models import SignatureModel
from datetime import date


class InvoiceQuerySet(models.QuerySet):
    def outstanding(self):
        # Subquery - get a list of invoices with ledger totals > 0
        # The performance may get worse as the number of invoices increases, in which case, it may be faster if the
        #   subquery uses an outer reference, rather than being a big 'IN' check
        outstanding = models.Subquery(
            Invoice.objects.annotate(
                balance=models.Sum('allocated_ledger_items__amount')
            ).filter(balance__gt=0).values('id')
        )

        # Apply a filter to the queryset, limiting it to those outstanding invoices, plus check they're overdue
        return self.filter(id__in=outstanding)

    def overdue(self):
        # Overdue only applies to outstanding
        return self.outstanding().filter(due_date__lt=date.today())


class Invoice(SignatureModel):
    number = models.IntegerField(unique=True)
    prefix = models.CharField(max_length=32, blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    fao = models.CharField(max_length=128, blank=True, null=True)
    invoiced_to = models.CharField(max_length=128, blank=True, null=True)
    line1 = models.CharField(max_length=128, blank=True, null=True)
    line2 = models.CharField(max_length=128, blank=True, null=True)
    line3 = models.CharField(max_length=128, blank=True, null=True)
    town = models.CharField(max_length=64, blank=True, null=True)
    countystate = models.CharField(max_length=64, blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    postcode = models.CharField(max_length=32, blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    custom_narrative = models.BooleanField()
    narrative = models.TextField(blank=True, null=True)
    ref_no = models.CharField(max_length=64, blank=True, null=True)
    division = models.IntegerField(blank=True, null=True)
    allocation = models.IntegerField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True, db_column='duedate')
    contact_person = models.CharField(max_length=128, blank=True, null=True)
    contact_email = models.CharField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=64, blank=True, null=True)
    company = models.CharField(max_length=128, blank=True, null=True)
    formatted_addressee = models.TextField(blank=True, null=True)
    referred = models.BooleanField()
    vat_no = models.CharField(max_length=64, blank=True, null=True)

    ledger_items = models.ManyToManyField(
        'Ledger', through='InvoiceLedger', through_fields=('invoice', 'ledger')
    )

    # Artificial many-to-many to support our obsolete credit note allocation nonsense
    allocated_ledger_items = models.ManyToManyField(
        'Ledger', through='InvoiceLedger', through_fields=('allocation', 'ledger'), related_name='allocated_invoice'
    )

    objects = InvoiceQuerySet.as_manager()

    class Meta:
        managed = False
        db_table = '[app].[invoice]'

    def get_absolute_url(self):
        return reverse('invoice:view', args=[self.id])

    @property
    def full_number(self):
        return f'{self.prefix}{self.number}'

    def balance(self):
        return self.allocated_ledger_items.aggregate(sum=models.Sum('amount'))['sum']


class InvoiceLedger(models.Model):
    ledger = models.ForeignKey('Ledger', models.DO_NOTHING, db_column='ledger', related_name='invoice_ledger')
    invoice = models.ForeignKey(Invoice, models.DO_NOTHING, db_column='invoice', related_name='invoice_ledger')
    # Awful backwards-compatibility. Allocation was used some items on some invoices ("credit notes") paid off others?!
    allocation = models.ForeignKey(Invoice, models.DO_NOTHING, db_column='allocation', to_field='number', related_name='invoice_ledger_allocations')
    item_no = models.IntegerField(blank=True, null=True)
    # type = models.ForeignKey('TransactionType', models.DO_NOTHING, db_column='type', blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[app].[invoice_ledger]'


class Ledger(models.Model):
    date = models.DateTimeField(blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    finance_code = models.CharField(max_length=64, blank=True, null=True)
    narrative = models.CharField(max_length=128, blank=True, null=True)
    # division = models.ForeignKey(Division, models.DO_NOTHING, db_column='division', blank=True, null=True)
    # type = models.ForeignKey('TransactionType', models.DO_NOTHING, db_column='type', blank=True, null=True)
    # account = models.ForeignKey('LedgerAccount', models.DO_NOTHING, db_column='account', blank=True, null=True)
    # enrolment = models.ForeignKey(Enrolment, models.DO_NOTHING, db_column='enrolment', blank=True, null=True)

    allocation = models.IntegerField(blank=True, null=True)
    ref_no = models.IntegerField(blank=True, null=True)
    batch = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[app].[ledger]'
