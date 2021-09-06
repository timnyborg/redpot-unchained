from typing import Optional

import django_tables2 as tables

from django import http
from django.urls import reverse

from apps.amendment.models import Amendment
from apps.core.utils.datatables import DeleteLinkColumn, EditLinkColumn, LinkColumn, PoundsColumn
from apps.finance.models import Ledger


class LedgerDeleteColumn(DeleteLinkColumn):
    """A customized delete column that links and renders based on a per-user check"""

    def render(self, value: int, record: Ledger, table) -> str:
        # todo: consider whether confirmation is better as a modal
        if record.user_can_delete(user=table.request.user):
            return super().render(value)
        return ''

    def linkify(self, value: int, record, table) -> Optional[str]:
        if record.user_can_delete(user=table.request.user):
            return super().linkify(record=record) + f'?next={table.request.path}'
        return None


class PrintLinkColumn(LinkColumn):
    """Display a print link if if a record is a payment"""

    icon = 'print'
    attrs = {"a": {"target": "_blank"}}  # new window.  todo: check if this is necessary once PDF rendering is in place

    def linkify(self, record: Ledger) -> Optional[str]:
        if record.type.is_cash:
            return reverse(
                'finance:receipt', kwargs={'allocation': record.allocation, 'enrolment_id': record.enrolment_id}
            )
        return None

    def render(self, record) -> str:
        if record.type.is_cash:
            return super().render(record)
        return ''


class FinanceTable(tables.Table):
    """Display's an enrolment's financial history, with options to print or delete rows
    Requires `request=` to be passed, in order to dynamically display delete rows
    """

    request: http.HttpRequest
    # todo: print-receipt column w/ display logic
    amount = PoundsColumn()
    invoice = tables.Column(
        verbose_name='Invoice',
        accessor='invoice_ledger__invoice',
        linkify=True,
    )
    delete = LedgerDeleteColumn(verbose_name='')
    print = PrintLinkColumn(verbose_name='')

    def render_batch(self, value, bound_column) -> str:
        return value or bound_column.default  # handle historic 0s

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
