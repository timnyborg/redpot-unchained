import re
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import FormMixin

from apps.core.utils import strings
from apps.core.utils.urls import next_url_if_safe
from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin
from apps.enrolment.models import Enrolment
from apps.finance.models import Ledger
from apps.student.models import Student

from . import datatables, forms, models, pdfs, services


class Search(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, FormMixin, FilterView):
    template_name = 'invoice/search.html'
    model = models.Invoice
    table_class = datatables.InvoiceSearchTable
    filterset_class = datatables.InvoiceSearchFilter
    subtitle = 'Search'
    form_class = forms.LookupForm


class Lookup(LoginRequiredMixin, generic.View):
    """Redirects to an invoice matching `number` with or without EQ prefix.
    When not found, sends the user back to /search
    """

    def post(self, request) -> http.HttpResponse:
        try:
            # Extract the invoice number, ignoring the prefix and any trailing whitespace
            match = re.fullmatch(r'[A-z]{0,2}(\d+)\s*', request.POST['number'])
            if not match:
                raise models.Invoice.DoesNotExist()
            invoice_number = match.group(1)
            invoice = models.Invoice.objects.get(number=invoice_number)
            return redirect(invoice)
        except models.Invoice.DoesNotExist:
            messages.error(request, 'Invoice not found')
            return redirect('invoice:search')


class View(LoginRequiredMixin, PageTitleMixin, generic.DetailView):
    template_name = 'invoice/view.html'
    model = models.Invoice

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        fees = self.object.get_fees().select_related('enrolment__module', 'type')
        fee_table = datatables.InvoiceFeesTable(fees, prefix="fees-", request=self.request)

        credits = self.object.get_payments().non_cash().select_related('enrolment__module', 'type')
        credit_table = datatables.InvoicePaymentsTable(credits, prefix="credits-", request=self.request)

        payments = self.object.get_payments().cash().select_related('enrolment__module', 'type')
        payment_table = datatables.InvoicePaymentsTable(payments, prefix="payments-", request=self.request)

        credit_notes = self.object.get_credit_note_items().non_cash().select_related('enrolment__module', 'type')
        credit_note_table = datatables.InvoiceCreditNoteTable(
            credit_notes, prefix="credit-notes-", request=self.request
        )

        try:
            plan = self.object.payment_plan
            schedule_table = datatables.PaymentScheduleTable(plan.scheduled_payments.all())
        except ObjectDoesNotExist:
            plan = None
            schedule_table = None

        return {
            **kwargs,
            'fee_table': fee_table,
            'credit_table': credit_table,
            'credit_note_table': credit_note_table,
            'payment_table': payment_table,
            'plan': plan,
            'schedule_table': schedule_table,
        }


class Edit(PermissionRequiredMixin, AutoTimestampMixin, SuccessMessageMixin, PageTitleMixin, generic.UpdateView):
    model = models.Invoice
    form_class = forms.InvoiceForm
    template_name = 'core/form.html'
    permission_required = 'invoice.change_invoice'
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
        int_ids = [int(str_id) for str_id in self.request.GET.getlist('enrolment') if str_id.isnumeric()]
        return (
            Enrolment.objects.filter(
                # Past year of enrolments, plus any indicated by URL
                Q(created_on__gt=datetime.now() - relativedelta(years=1)) | Q(id__in=int_ids),
                qa__student=self.student,
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
            Ledger.objects.filter(
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
        self.amount = self.fees.total()
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self) -> dict:
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


class UploadRCP(PermissionRequiredMixin, PageTitleMixin, generic.FormView):
    permission_required = 'invoice.upload_rcp'
    form_class = forms.UploadRCPForm
    template_name = 'core/form.html'
    title = 'Repeating card payments'
    subtitle = 'Upload'

    def form_valid(self, form):
        try:
            payments_added = services.add_repeating_payments_from_file(file=form.cleaned_data['file'])
        except UnicodeDecodeError:
            form.add_error('file', 'Invalid file uploaded')
            return self.form_invalid(form)

        if payments_added:
            messages.success(self.request, f'{payments_added} payment(s) added')
        else:
            messages.warning(self.request, 'No payments added.  Ensure you have a valid file')

        return super().form_valid(form)

    def get_success_url(self):
        return self.request.get_full_path()  # self-redirect


class EditPaymentPlan(
    PermissionRequiredMixin, SuccessMessageMixin, AutoTimestampMixin, PageTitleMixin, generic.UpdateView
):
    permission_required = 'invoice.change_paymentplan'
    model = models.PaymentPlan
    form_class = forms.PaymentPlanForm
    template_name = 'core/form.html'
    success_message = 'Payment plan updated'

    def get_subtitle(self):
        return f'Edit – {self.object.invoice}'

    def get_success_url(self):
        return self.object.invoice.get_absolute_url() + '#schedule'


class CreatePaymentPlan(
    PermissionRequiredMixin, SuccessMessageMixin, AutoTimestampMixin, PageTitleMixin, generic.CreateView
):
    permission_required = 'invoice.add_paymentplan'
    model = models.PaymentPlan
    form_class = forms.PaymentPlanForm
    template_name = 'core/form.html'
    success_message = 'Payment plan updated'

    def dispatch(self, request, *args, **kwargs):
        # Check there's no existing plan
        self.invoice = get_object_or_404(models.Invoice, pk=self.kwargs['invoice_id'], payment_plan__isnull=True)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {
            'invoice': self.invoice,
            'amount': self.invoice.balance,
            'type': models.CUSTOM_TYPE,
            'status': models.PaymentPlan.Statuses.PENDING_CUSTOM,
        }

    def get_subtitle(self):
        return f'Create – {self.invoice}'

    def get_success_url(self):
        return reverse('invoice:edit-payment-schedule', args=[self.object.pk])


class EditSchedule(PermissionRequiredMixin, PageTitleMixin, generic.DetailView):
    queryset = models.PaymentPlan.objects.prefetch_related('scheduled_payments')
    template_name = 'invoice/edit_schedule.html'
    permission_required = 'invoice.add_paymentplan'

    def get_subtitle(self):
        return f'Edit schedule – {self.object.invoice}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule'] = list(self.object.scheduled_payments.values('due_date', 'amount', 'is_deposit'))
        return context


class Credit(PermissionRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.FormView):
    """Form to credit an invoice on a single enrolment"""

    permission_required = 'invoice.credit_invoice'
    title = 'Invoice'
    subtitle = 'Credit'
    form_class = forms.CreditForm
    template_name = 'core/form.html'
    success_message = 'Invoice credited £%(amount).2f'

    def dispatch(self, request, *args, **kwargs):
        self.invoice = get_object_or_404(models.Invoice, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {**kwargs, 'invoice': self.invoice}

    def form_valid(self, form):
        services.add_credit(
            invoice=self.invoice,
            enrolment=form.cleaned_data['enrolment'],
            narrative=form.cleaned_data['narrative'],
            amount=form.cleaned_data['amount'],
            account_code=form.cleaned_data['account'].code,
            type_id=form.cleaned_data['type'].id,
            user=self.request.user,
        )
        return super().form_valid(form)

    def get_success_url(self):
        return next_url_if_safe(self.request) or self.invoice.get_absolute_url()


class SelectForPayment(PermissionRequiredMixin, PageTitleMixin, generic.FormView):
    """Form to select an invoice for payment before forwarding to Payment"""

    permission_required = 'invoice.pay_invoice'
    form_class = forms.SelectForPaymentForm
    template_name = 'core/form.html'
    title = 'Invoice'
    subtitle = 'Payment – Select invoice'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {
            **kwargs,
            'student': get_object_or_404(Student, pk=self.kwargs['student_id']),
            # We want to let finance users post adjustments to paid invoices,
            # but keep the list clean of paid invoices for regular users
            'exclude_paid': not self.request.user.has_perm('core.finance'),
        }

    def form_valid(self, form) -> http.HttpResponse:
        return redirect('invoice:payment', pk=form.cleaned_data['invoice'].pk)


class Payment(PermissionRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.FormView):
    """Form to credit an invoice on a single enrolment"""

    permission_required = 'invoice.pay_invoice'
    title = 'Invoice'
    form_class = forms.PaymentForm
    template_name = 'core/form.html'
    success_message = 'Payment added: £%(amount).2f'

    def dispatch(self, request, *args, **kwargs):
        self.invoice = get_object_or_404(models.Invoice, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_subtitle(self):
        return f'Add payment – {self.invoice}'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {**kwargs, 'invoice': self.invoice}

    def form_valid(self, form):
        services.add_payment(
            invoice=self.invoice,
            enrolment=form.cleaned_data['enrolment'],
            narrative=form.cleaned_data['narrative'],
            amount=form.cleaned_data['amount'],
            type_id=form.cleaned_data['type'].id,
            user=self.request.user,
        )
        return super().form_valid(form)

    def get_success_url(self):
        return next_url_if_safe(self.request) or self.invoice.get_absolute_url()


class PDF(PermissionRequiredMixin, generic.View):
    """Generate a transcript for a single student"""

    permission_required = 'invoice.print_invoice'

    def get(self, request, pk: int, *args, **kwargs) -> http.HttpResponse:
        invoice = get_object_or_404(models.Invoice, pk=pk)
        document = pdfs.create_invoice(invoice)

        filename = strings.normalize(f'Invoice_{invoice}{invoice.invoiced_to}.pdf').replace(' ', '_')
        return http.HttpResponse(
            document, content_type='application/pdf', headers={'Content-Disposition': f'inline;filename={filename}'}
        )


class StatementPDF(PermissionRequiredMixin, generic.View):
    """Generate a transcript for a single student"""

    permission_required = 'invoice.print_invoice'

    def get(self, request, pk: int, *args, **kwargs) -> http.HttpResponse:
        invoice = get_object_or_404(models.Invoice, pk=pk)
        document = pdfs.create_statement(invoice)

        filename = f'Invoice_Statement_{invoice.prefix}{invoice.number}.pdf'
        return http.HttpResponse(
            document, content_type='application/pdf', headers={'Content-Disposition': f'inline;filename={filename}'}
        )
