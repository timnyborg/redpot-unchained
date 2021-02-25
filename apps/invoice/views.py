from django_tables2.views import SingleTableMixin, RequestConfig
from django_filters.views import FilterView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.detail import DetailView

from apps.core.utils.views import PageTitleMixin

from .models import Invoice
from .datatables import (
    InvoiceSearchFilter, InvoiceSearchTable, InvoiceFeesTable, InvoicePaymentsTable, PaymentScheduleTable
)


class Search(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    template_name = 'invoice/search.html'
    model = Invoice
    table_class = InvoiceSearchTable
    filterset_class = InvoiceSearchFilter
    subtitle = 'Search'


class View(LoginRequiredMixin, PageTitleMixin, DetailView):
    template_name = 'invoice/view.html'
    model = Invoice

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        fees = self.object.get_fees().select_related('enrolment__module', 'type')
        fee_table = InvoiceFeesTable(fees, prefix="fees-")
        RequestConfig(self.request).configure(fee_table)  # Enables sorting, in lieu of the MultiTableMixin

        payments = self.object.get_payments().select_related('enrolment__module', 'type')
        payment_table = InvoicePaymentsTable(payments, prefix="payments-")
        RequestConfig(self.request).configure(payment_table)

        try:
            plan = self.object.payment_plan
            schedule_table = PaymentScheduleTable(plan.schedule.all())
        except ObjectDoesNotExist:
            plan = None
            schedule_table = None

        return {
            **kwargs,
            'fee_table': fee_table,
            'payment_table': payment_table,
            'plan': plan,
            'schedule_table': schedule_table
        }
