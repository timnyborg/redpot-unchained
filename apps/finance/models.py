from datetime import date
from decimal import Decimal
from typing import Optional

from django.db import models
from django.urls import reverse

from apps.core.models import SignatureModel, User


class Accounts(models.TextChoices):
    """Non-exhaustive enum of accounts, including those commonly used in business logic"""

    # Debtor control, which forms the other side of all debt transactions (adding/removing fees)
    DEBTOR = 'Z300', 'Debtor control'
    # Cash control, which forms the other side of all cash transactions (payments/refunds)
    CASH = 'ZY00', 'Cash control'
    TUITION = '43310', 'Tuition'


class TransactionTypes(models.IntegerChoices):
    """Non-exhaustive enum of transaction types, including those commonly used in business logic"""

    FEE = 1, 'Fee'
    CREDIT_CARD = 13, 'Credit card'
    ONLINE = 16, 'Online'
    RCP = 17, 'Repeating card payment'
    WRITEOFF = 99, 'Write-off'


class LedgerQuerySet(models.QuerySet):
    def debts(self) -> models.QuerySet:
        """Returns only those on the debtor control side of the ledger"""
        return self.filter(account=Accounts.DEBTOR)

    def cash_control(self) -> models.QuerySet:
        """Returns only those on the 'cash control' (non-debtor control) side of the ledger"""
        return self.filter(account=Accounts.CASH)

    def invoiced(self) -> models.QuerySet:
        return self.filter(invoice_ledger__id__isnull=False)

    def uninvoiced(self) -> models.QuerySet:
        return self.filter(invoice_ledger__id__isnull=True)

    def total(self) -> Optional[Decimal]:
        """Convenience function to get the sum of the queryset"""
        # todo: should the `or Decimal(0)` go in here, making it non optional?
        return self.aggregate(balance=models.Sum('amount'))['balance']

    # Todo: consider renaming payments and non-payments?
    def non_cash(self) -> models.QuerySet:
        return self.filter(type__is_cash=False)

    def cash(self) -> models.QuerySet:
        return self.filter(type__is_cash=True)

    def batched(self) -> models.QuerySet:
        # todo: rely on isnull once all applications set null rather than 0
        return self.filter(batch__gt=0)

    def unbatched(self) -> models.QuerySet:
        # Todo: remove the batch=0 option once all applications creating rows use null
        return self.filter(models.Q(batch=0) | models.Q(batch__isnull=True))


class Ledger(SignatureModel):
    # `timestamp` records the actual date of a transaction, which may differ from created_on (instalments, backfilling)
    timestamp = models.DateTimeField(db_column='date', verbose_name='Date')
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    finance_code = models.CharField(max_length=64, blank=True, null=True)
    narrative = models.CharField(max_length=128)
    # todo: investigate if this (division) has value
    division = models.ForeignKey('core.Division', models.PROTECT, db_column='division', blank=True, null=True)
    type = models.ForeignKey('TransactionType', models.PROTECT, db_column='type')
    account = models.ForeignKey('Account', models.PROTECT, db_column='account', limit_choices_to={'is_hidden': False})
    enrolment = models.ForeignKey('enrolment.Enrolment', models.PROTECT, db_column='enrolment', blank=True, null=True)
    allocation = models.IntegerField()
    ref_no = models.IntegerField(blank=True, null=True)
    batch = models.IntegerField(blank=True, null=True)

    objects = LedgerQuerySet.as_manager()

    class Meta:
        db_table = 'ledger'
        permissions = [('print_receipt', 'Can print receipts for payments')]

    def get_delete_url(self) -> str:
        return reverse('finance:delete-transaction', kwargs={'allocation': self.allocation})

    def user_can_delete(self, *, user: User) -> bool:
        """Determine if a user is allowed to remove an entry from the ledger"""
        return (
            # Devs can always delete
            user.has_perm('finance.delete_ledger')
            # Same-day, own-entry deletion for others
            or self.created_by == user.username
            and self.timestamp.date() == date.today()
            # No deleting fee items attached to invoices
            and not (hasattr(self, 'invoice_ledger') and not self.type.is_cash)
        )


class Account(models.Model):
    code = models.CharField(primary_key=True, max_length=5)
    description = models.CharField(max_length=64)
    is_hidden = models.BooleanField()  # todo: convert to is_active for consistency

    class Meta:
        db_table = 'ledger_account'

    def __str__(self) -> str:
        return str(self.description)


class TransactionType(models.Model):
    description = models.CharField(max_length=32)
    is_cash = models.BooleanField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'transaction_type'

    def __str__(self) -> str:
        return str(self.description)
