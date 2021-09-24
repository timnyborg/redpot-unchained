from datetime import datetime
from urllib.parse import urlencode

from dateutil.relativedelta import relativedelta
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_list_or_404, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from apps.core.utils import strings
from apps.core.utils.urls import next_url_if_safe
from apps.core.utils.views import PageTitleMixin
from apps.enrolment.models import Enrolment
from apps.fee.models import Fee
from apps.student.models import Student

from . import datatables, forms, models, pdfs, services


class AddFees(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, SingleTableMixin, generic.FormView):
    """A two part view for adding fees to an enrolment.  Includes a self-submitting form for bespoke fees,
    and a datatable which posts to AddModuleFees
    """

    form_class = forms.AddFeeForm
    initial = {'type': models.TransactionTypes.FEE}
    table_class = datatables.AddFeesTable
    template_name = 'finance/add_fees.html'
    title = 'Finance'
    success_message = 'Payment recorded (£%(amount).2f)'

    def get_subtitle(self):
        return f'Add fees – {self.enrolment.qa.student} on {self.enrolment.module}'

    def dispatch(self, request, *args, **kwargs):
        self.enrolment = get_object_or_404(Enrolment, pk=self.kwargs['enrolment_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_table_data(self):
        return self.enrolment.module.fees.all()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {'editable_type': self.request.user.has_perm('finance'), **kwargs}  # todo: actual permission

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return {**context, 'enrolment': self.enrolment}

    def form_valid(self, form):
        services.insert_ledger(
            account_code=form.cleaned_data['account'].code,
            amount=form.cleaned_data['amount'],
            user=self.request.user,
            finance_code=self.enrolment.module.finance_code,
            narrative=form.cleaned_data['narrative'],
            enrolment_id=self.enrolment.id,
            type_id=form.cleaned_data['type'].id,
        )
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return next_url_if_safe(self.request) or self.enrolment.get_absolute_url()


class AddPayment(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, generic.FormView):
    form_class = forms.AddPaymentForm
    title = 'Finance'
    template_name = 'finance/add_payment.html'
    success_message = 'Payment recorded (£%(amount).2f)'

    def get_subtitle(self):
        return f'Add payment – {self.enrolment.qa.student} on {self.enrolment.module}'

    def dispatch(self, request, *args, **kwargs):
        self.enrolment = get_object_or_404(Enrolment, pk=self.kwargs['enrolment_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enrolment'] = self.enrolment
        return context

    def form_valid(self, form):
        services.insert_ledger(
            account_code=models.Accounts.CASH,
            amount=-form.cleaned_data['amount'],
            user=self.request.user,
            finance_code=self.enrolment.module.finance_code,
            narrative=form.cleaned_data['narrative'],
            enrolment_id=self.enrolment.id,
            type_id=form.cleaned_data['type'].id,
        )
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return next_url_if_safe(self.request) or self.enrolment.get_absolute_url()


class AddModuleFees(LoginRequiredMixin, generic.View):
    """POST endpoint for AddFees' table.  Can add multiple fees to an enrolment"""

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        enrolment = get_object_or_404(Enrolment, pk=self.kwargs['enrolment_id'])
        fee_ids = request.POST.getlist('fee')
        fees = Fee.objects.filter(id__in=fee_ids, module_id=enrolment.module_id)
        if not fees:
            messages.warning(request, 'You must select a fee')
            return redirect(reverse('finance:add-fees', args=[enrolment.pk]))

        for fee in fees:
            services.add_enrolment_fee(enrolment_id=enrolment.id, fee_id=fee.id, user=request.user)
        messages.success(request, f'{len(fees)} fees added')
        return redirect(enrolment.get_absolute_url())


class MultipleEnrolmentSelection(LoginRequiredMixin, PageTitleMixin, generic.TemplateView):
    """User chooses enrolments from a student's recent OR the user's recently created enrolments
    Then passes the selections to MultipleEnrolmentPayment
    """

    title = 'Finance'
    subtitle = 'Multiple enrolment payment'
    template_name = 'finance/multiple_enrolment_selection.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = get_object_or_404(Student, pk=self.kwargs['student_id'])

        student_enrolments = Enrolment.objects.outstanding().filter(
            qa__student=student, created_on__gt=datetime.now() - relativedelta(years=3)
        )
        student_enrolments_table = datatables.OutstandingEnrolmentsTable(student_enrolments)

        one_month_ago = datetime.now() - relativedelta(months=1)
        recent_enrolments = Enrolment.objects.outstanding().filter(
            (
                Q(created_by=self.request.user.username, created_on__gt=one_month_ago)
                | Q(modified_by=self.request.user.username, modified_on__gt=one_month_ago)
            ),
        )
        recent_enrolments_table = datatables.OutstandingEnrolmentsTable(recent_enrolments)

        return {
            **context,
            'student_enrolments_table': student_enrolments_table,
            'recent_enrolments_table': recent_enrolments_table,
        }

    def post(self, request, *args, **kwargs):
        enrolments = request.POST.getlist('enrolment')
        if not Enrolment.objects.filter(id__in=enrolments).exists():
            messages.error(request, 'You must select an enrolment')
            return self.get(request, *args, **kwargs)

        query_string = urlencode(
            {'enrolment': enrolments, 'next': reverse('student-view', args=[self.kwargs['student_id']])}, doseq=True
        )
        return redirect(reverse('finance:pay-multiple-enrolments') + f'?{query_string}')


class MultipleEnrolmentPayment(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, generic.FormView):
    """User distributes a payment between multiple enrolments"""

    title = 'Finance'
    subtitle = 'Multiple enrolment payment – allocation'
    template_name = 'core/form.html'
    form_class = forms.MultipleEnrolmentPaymentForm
    success_message = 'Payment added'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['enrolments'] = get_list_or_404(Enrolment, id__in=self.request.GET.getlist('enrolment'))
        return kwargs

    def form_valid(self, form):
        services.add_distributed_payment(
            narrative=form.cleaned_data['narrative'],
            amount=form.cleaned_data['amount'],
            type_id=form.cleaned_data['type'].id,
            user=self.request.user,
            enrolments=form.cleaned_data['allocations'],
        )
        return super().form_valid(form)

    def get_success_url(self):
        return next_url_if_safe(self.request) or '/'  # todo: where should this go if no next?


class Transfer(LoginRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.FormView):
    form_class = forms.TransferForm
    template_name = 'core/form.html'
    title = 'Finance'
    success_message = '£%(amount).2f transferred'

    def dispatch(self, request, *args, **kwargs):
        self.source_enrolment = get_object_or_404(Enrolment, pk=self.kwargs['enrolment_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_subtitle(self):
        return f'Transfer – from {self.source_enrolment.qa.student} – {self.source_enrolment.module}'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {**kwargs, 'source_enrolment': self.source_enrolment}

    def form_valid(self, form):
        services.transfer_funds(
            source_enrolment=self.source_enrolment,
            target_enrolment=form.cleaned_data['target_enrolment'],
            amount=form.cleaned_data['amount'],
            type_id=form.cleaned_data['type'].id,
            narrative=form.cleaned_data['narrative'],
            user=self.request.user,
        )
        return super().form_valid(form)

    def get_success_url(self):
        return self.source_enrolment.get_absolute_url()


class DeleteTransaction(LoginRequiredMixin, PageTitleMixin, generic.TemplateView):
    """Delete a transaction from the ledger (an allocation - both sides of the ledger)
    Acts like a DeleteView, with get() providing a confirmation form
    """

    template_name = 'core/delete_form.html'
    title = 'Finance'
    subtitle = 'Delete transaction'

    @transaction.atomic
    def post(self, request: http.HttpRequest, allocation: int, *args, **kwargs) -> http.HttpResponse:
        ledger_items = models.Ledger.objects.filter(allocation=allocation)
        if not ledger_items.exists():
            raise http.Http404
        if not ledger_items[0].user_can_delete(user=request.user):
            # Check permission to delete against one of the items (they will all have the same timestamp info)
            raise PermissionDenied("You don't have permission to delete this transaction")
        # dump the logging data before deletion
        data = [item.__dict__ for item in ledger_items]
        ledger_items.delete()
        # todo: consider a better form of logging this
        mail.send_mail(
            subject='Deleted ledger rows',
            from_email=settings.SUPPORT_EMAIL,
            recipient_list=[settings.SUPPORT_EMAIL],
            message=f'User {request.user.username} deleted rows with the following data: {data}',
        )
        messages.success(request, 'Transaction deleted')
        return redirect(next_url_if_safe(request) or '')


class ReceiptPDF(PermissionRequiredMixin, generic.View):
    """Generate a transcript for a single student"""

    permission_required = 'finance.print_receipt'

    def get(self, request, allocation: int, enrolment_id: int, *args, **kwargs) -> http.HttpResponse:
        enrolment = get_object_or_404(Enrolment, pk=enrolment_id)
        student = enrolment.qa.student
        document = pdfs.create_receipt(allocation=allocation, student=student)
        filename = strings.normalize(f'Receipt_{allocation}_{student.firstname}_{student.surname}.pdf')
        return http.HttpResponse(
            document, content_type='application/pdf', headers={'Content-Disposition': f'inline;filename={filename}'}
        )


# ------------ Transaction batching operations -----------------

# todo: review all batch functionality, and see how well it actually matches business needs.  It's all old and janky


class AllBatches(PermissionRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    """Lists batches of financial transactions, plus unbatched items"""

    permission_required = 'finance'  # todo: real finance permission
    table_class = datatables.BatchTable
    filterset_class = datatables.BatchFilter
    template_name = 'core/search.html'
    # .values + .distinct queryset lets us display grouped results in the table, but related labels must be included
    queryset = models.Ledger.objects.cash().values('created_by', 'type', 'type__description', 'batch').distinct()


class CreateBatch(generic.View):
    # Todo: convert to post once the table is rigged up to have a posting link column
    def get(self, request, type_id: int, created_by: str, *args, **kwargs) -> http.HttpResponse:
        """Assign a batch # to a set of transactions of a shared type owned by a given user"""
        batch: int = services.next_batch()
        models.Ledger.objects.unbatched().filter(
            created_by=created_by,
            type_id=type_id,
        ).update(batch=batch)
        return redirect(reverse('finance:print-batch', args=[batch]))


class PrintBatch(generic.TemplateView):
    """Produces a printable list of transactions in a batch"""

    # todo: possibly move this view to a square report, depending on its use
    template_name = 'finance/print_batch.html'

    def get_context_data(self, **kwargs) -> dict:
        batch = self.kwargs['batch']

        # Find payments on a batch
        # The cash side items are not linked to enrolments, and are the total payment
        cash_control_lines = models.Ledger.objects.filter(batch=batch).cash_control().select_related('type')

        # The debtor side items are split among enrolments, and tally to equal the cash side
        debtor_control_lines = get_list_or_404(
            models.Ledger.objects.filter(batch=batch)
            .debts()
            .select_related('enrolment__module', 'enrolment__qa__student', 'invoice_ledger__invoice')
            .order_by('timestamp')
        )

        # Link up the sides of the transactions
        transactions = [
            {
                'cash_line': cash_line,
                'debtor_lines': [line for line in debtor_control_lines if line.allocation == cash_line.allocation],
            }
            for cash_line in cash_control_lines
        ]

        return {
            'batch': batch,
            'transactions': transactions,
            'total': sum(line.amount for line in cash_control_lines),
        }
