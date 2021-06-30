from django_filters.views import FilterView
from django_tables2.views import RequestConfig, SingleTableMixin

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import FormMixin

from apps.core.utils.views import PageTitleMixin

from . import datatables, forms
from .models import Invoice


class Search(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, FormMixin, FilterView):
    template_name = 'invoice/search.html'
    model = Invoice
    table_class = datatables.InvoiceSearchTable
    filterset_class = datatables.InvoiceSearchFilter
    subtitle = 'Search'
    form_class = forms.LookupForm


class Lookup(generic.View):
    """Redirects to an invoice matching `number` with or without EQ prefix.
    When not found, sends the user back to /search
    """

    http_method_names = ['post']

    def post(self, request):
        invnum = request.POST['number']
        if not invnum.isdigit():
            # If they've included a prefix (eg EQ), strip it out
            invnum = invnum[2:]

        try:
            invoice = Invoice.objects.get(number=invnum)
            return redirect(invoice.get_absolute_url())
        except (Invoice.DoesNotExist, ValueError):
            messages.error(request, 'Invoice not found')
            return redirect(reverse('invoice:search'))


class View(LoginRequiredMixin, PageTitleMixin, generic.DetailView):
    template_name = 'invoice/view.html'
    model = Invoice

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        fees = self.object.get_fees().select_related('enrolment__module', 'type')
        fee_table = datatables.InvoiceFeesTable(fees, prefix="fees-")
        RequestConfig(self.request).configure(fee_table)  # Enables sorting, in lieu of the MultiTableMixin

        payments = self.object.get_payments().select_related('enrolment__module', 'type')
        payment_table = datatables.InvoicePaymentsTable(payments, prefix="payments-")
        RequestConfig(self.request).configure(payment_table)

        try:
            plan = self.object.payment_plan
            schedule_table = datatables.PaymentScheduleTable(plan.schedule.all())
        except ObjectDoesNotExist:
            plan = None
            schedule_table = None

        return {
            **kwargs,
            'fee_table': fee_table,
            'payment_table': payment_table,
            'plan': plan,
            'schedule_table': schedule_table,
        }


class Edit(PermissionRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.UpdateView):
    model = Invoice
    form_class = forms.EditForm
    template_name = 'core/form.html'
    permission_required = 'invoice.edit'
    permission_denied_message = 'Only members of Finance can edit invoices'
    success_message = 'Invoice updated'
