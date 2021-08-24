import django_tables2 as tables

from apps.amendment.models import Amendment
from apps.core.utils.datatables import EditLinkColumn, PoundsColumn
from apps.finance.models import Ledger


class FinanceTable(tables.Table):
    # todo: print-receipt and delete columns, w/ display logic
    amount = PoundsColumn()
    invoice = tables.Column(
        verbose_name='Invoice',
        accessor='invoice_ledger__invoice',
        linkify=True,
    )

    def render_batch(self, value):
        return value or '—'

    class Meta:
        model = Ledger
        fields = ['amount', 'narrative', 'type', 'timestamp', 'invoice', 'allocation', 'batch', 'print', 'delete']
        template_name = 'django_tables2/bootstrap.html'

    def __init__(self, display_finance_columns=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not display_finance_columns:
            self.columns['allocation'].column.visible = False
            self.columns['batch'].column.visible = False


class AmendmentTable(tables.Table):
    amount = PoundsColumn()
    edit = EditLinkColumn(verbose_name='')

    class Meta:
        model = Amendment
        fields = ['type', 'amount', 'requested_by', 'requested_on', 'approved_by', 'approved_on', 'status', 'edit']
        template_name = 'django_tables2/bootstrap.html'
