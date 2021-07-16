import django_tables2 as tables

from apps.core.utils.datatables import PoundsColumn
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


#
#     finance_grid = SQLFORM.grid(
#         finance_query,
#
#         left=idb.invoice_ledger.on(idb.invoice_ledger.ledger == idb.ledger.id),
#         fields=grid_fields,
#         orderby=idb.ledger.date,
#         maxtextlength=130,
#         args=request.args[:1],
#         links=[delete_link,
#                lambda row: A(icon('print'),
#                              _href=URL('finance', 'receipt', args=[row.ledger.allocation, student]),
#                              _target='_blank',
#                              ) if row.transaction_type.is_cash else None,
#                # This doesn't handle both sides...
#                # lambda row: A(icon('pencil'),
#                #              href=URL('appadmin', 'update', args=['idb', 'ledger', row.ledger.id],
#                                   vars={'_next': URL(args=request.args, vars=request.vars)}),
#                #              )
#                ],
#         **minimal_form_settings
#     )


class AmendmentTable(tables.Table):
    pass

    # if idb(idb.amendment.enrolment == enrolment.id):
    #     amendment_fields = [idb.amendment.id, idb.amendment_type.type, idb.amendment.amount,
    #                         idb.amendment.requested_by, idb.amendment.requested_on,
    #                         idb.amendment.approved_by, idb.amendment.approved_on, idb.amendment.status]
    #
    #     idb.amendment.requested_by.readable = True
    #     idb.amendment.requested_on.readable = True
    #     idb.amendment.approved_by.readable = True
    #     idb.amendment.approved_on.readable = True
    #     idb.amendment.status.readable = True
    #
    #     amendment_grid = SQLFORM.grid(
    #         ((idb.amendment.enrolment == enrolment.id)
    #          & (idb.amendment_type.id == idb.amendment.type)
    #          & (idb.amendment.is_complete == False)),
    #         fields=amendment_fields,
    #         orderby=(idb.amendment.status, idb.amendment.requested_on),
    #         maxtextlength=130,
    #         links=[lambda row: A(icon('pencil'), _href=URL('amendment', 'edit', args=row.amendment.id))],
    #         **minimal_form_settings
    #     )
    # else:
    #     amendment_grid = None
