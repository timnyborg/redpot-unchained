from django_tables2 import RequestConfig

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.views import generic

from apps.core.utils.views import PageTitleMixin
from apps.finance.models import Ledger, TransactionTypes

from . import datatables, models


class View(LoginRequiredMixin, PageTitleMixin, generic.DetailView):
    """
    Multi-purpose view page for all aspect of an enrolment - details, finances, catering/accom bookings, etc.
    Redpot-legacy fused it all into enrolment/edit, but the edit form has been split off

    todo:
        modals (delete ledger, print amendment)
        cert printable logic (-> model)
        outstanding amendment table
        ledger deletion rules and icon display logic
        'payment allowed' logic
    """

    queryset = models.Enrolment.objects.select_related(
        'qa__student', 'module', 'status', 'result', 'qa__programme__qualification'
    ).prefetch_related(Prefetch('ledger_set', queryset=Ledger.objects.select_related('type', 'invoice_ledger')))
    template_name = 'enrolment/view.html'

    def get_subtitle(self):
        return f'View – {self.object.qa.student} on {self.object.module}'

    def has_payment_of_type(self, type: int) -> bool:
        """Checks whether any of the enrolment's payments match a given type, for determining amendment options"""
        return any(item.type_id == type for item in self.object.ledger_set.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['finance_table'] = datatables.FinanceTable(
            data=self.object.ledger_set.debts(),
            display_finance_columns=self.request.user.has_perm('finance'),  # todo: real permission
            prefix='finances-',
        )
        RequestConfig(self.request).configure(context['finance_table'])  # for pagination/sorting
        context['student'] = self.object.qa.student  # for brevity in template
        context['catering'] = self.object.catering.select_related('fee')
        context['accommodation'] = self.object.accommodation.select_related('limit')
        # Determine which amendments are possible, given the financial history of the enrolment
        amendment_options = {
            'online': self.has_payment_of_type(TransactionTypes.ONLINE),
            'credit_card': self.has_payment_of_type(TransactionTypes.CREDIT_CARD),
            'rcp': self.has_payment_of_type(TransactionTypes.RCP),
        }
        amendment_options['any'] = any(amendment_options.values())
        context['amendment_options'] = amendment_options
        return context
