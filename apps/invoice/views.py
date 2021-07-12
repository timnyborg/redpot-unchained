from datetime import datetime

from dateutil.relativedelta import relativedelta
from django_filters.views import FilterView
from django_tables2.views import RequestConfig, SingleTableMixin

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import FormMixin

from apps.core.utils.views import PageTitleMixin
from apps.enrolment.models import Enrolment
from apps.invoice.models import Ledger
from apps.student.models import Student

from . import datatables, forms, models, services
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
    form_class = forms.InvoiceForm
    template_name = 'core/form.html'
    permission_required = 'invoice.edit'
    permission_denied_message = 'Only members of Finance can edit invoices'
    success_message = 'Invoice updated'


class ChooseEnrolments(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, generic.TemplateView):
    """Step one for single-student, multiple enrolment invoices.
    They pick from a list of enrolments with uninvoiced entries then get sent to ChooseFees"""

    template_name = 'invoice/choose_enrolments.html'
    table_class = datatables.ChooseEnrolmentsTable
    title = 'Invoice'
    subtitle = 'Create – choose enrolments'

    def dispatch(self, request, *args, **kwargs):
        self.student = get_object_or_404(Student, pk=self.kwargs['student_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Enrolment.objects.filter(
                qa__student=self.student,
                created_on__gt=datetime.now() - relativedelta(years=1),
                # Only include enrolments with non-invoiced ledger items
                ledger__id__isnull=False,
                ledger__invoice_ledger__id__isnull=True,
            )
            .select_related('module')
            .distinct()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return {**context, 'student': self.student}


class ChooseFees(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, generic.TemplateView):
    """Step two for single-student, multiple enrolment invoices.
    They pick from a list of fees then get sent to Create"""

    template_name = 'invoice/choose_fees.html'
    table_class = datatables.ChooseFeesTable
    title = 'Invoice'
    subtitle = 'Create – choose fees'

    def dispatch(self, request, *args, **kwargs):
        self.student = get_object_or_404(Student, pk=self.kwargs['student_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            models.Ledger.objects.filter(
                enrolment__qa__student=self.student,
                enrolment__in=self.request.GET.getlist('enrolment'),
            )
            .debts()
            .uninvoiced()
            .select_related('type', 'enrolment__module')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return {**context, 'student': self.student}


class Create(LoginRequiredMixin, PageTitleMixin, generic.FormView):
    """Step three for single-student, multiple enrolment invoices.
    Provide the invoice details in a standard form"""

    form_class = forms.InvoiceForm
    template_name = 'core/form.html'
    title = 'Invoice'
    subtitle = 'Create – additional details'

    def dispatch(self, request, *args, **kwargs):
        fee_ids = request.GET.getlist('fee')
        self.student = get_object_or_404(Student, pk=kwargs['student_id'])
        self.fees = Ledger.objects.debts().uninvoiced().filter(pk__in=fee_ids, enrolment__qa__student=self.student)
        if not self.fees:
            raise http.Http404('No fees found')
        self.amount = self.fees.balance()
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        # Use the first fee to get default contact information
        module = self.fees[0].enrolment.module
        initial = {
            'invoiced_to': str(self.student),
            'due_date': datetime.today() + relativedelta(months=1),
            'contact_person': self.request.user.get_full_name(),
            'contact_email': module.email or module.portfolio.email,
            'contact_phone': module.phone or module.portfolio.phone,
        }
        billing_address = self.student.get_billing_address()
        if billing_address:
            for field in ['line1', 'line2', 'line3', 'town', 'countystate', 'country', 'postcode']:
                initial[field] = getattr(billing_address, field)
        return initial

    def form_valid(self, form):
        invoice = services.create_invoice(
            amount=self.amount,
            fees=self.fees,
            user=self.request.user,
            **form.cleaned_data,
        )
        messages.success(self.request, f'Invoice created: {invoice}')
        return redirect(invoice.get_absolute_url())
