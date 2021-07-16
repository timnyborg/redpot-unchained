from django_tables2.views import SingleTableMixin

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import generic

from apps.core.utils.views import PageTitleMixin
from apps.enrolment.models import Enrolment
from apps.fee.models import Fee

from . import datatables, forms, models, services


class AddFees(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, SingleTableMixin, generic.FormView):
    """A two part view for adding fees to an enrolment.  Includes a self-submitting form for bespoke fees,
    and a datatable which posts to AddModuleFees
    """

    form_class = forms.AddFeeForm
    initial = {'type': models.TransactionTypes.FEE}
    table_class = datatables.AddFeesTable
    template_name = 'finance/add_fees.html'
    title = 'Enrolment'
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
            account_id=form.cleaned_data['account'].code,
            amount=form.cleaned_data['amount'],
            user=self.request.user,
            finance_code=self.enrolment.module.finance_code,
            narrative=form.cleaned_data['narrative'],
            enrolment_id=self.enrolment.id,
            type_id=form.cleaned_data['type'].id,
        )
        return super().form_valid(form)

    def get_success_url(self):
        if url_has_allowed_host_and_scheme(self.request.GET.get('next'), allowed_hosts=None):
            return self.request.GET['next']
        return self.enrolment.get_absolute_url()


class AddPayment(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, generic.FormView):
    form_class = forms.AddPaymentForm
    title = 'Enrolment'
    template_name = 'core/form.html'
    success_message = 'Payment recorded (£%(amount).2f)'

    def get_subtitle(self):
        return f'Add payment – {self.enrolment.qa.student} on {self.enrolment.module}'

    def dispatch(self, request, *args, **kwargs):
        self.enrolment = get_object_or_404(Enrolment, pk=self.kwargs['enrolment_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        services.insert_ledger(
            account_id=models.Accounts.CASH,
            amount=-form.cleaned_data['amount'],
            user=self.request.user,
            finance_code=self.enrolment.module.finance_code,
            narrative=form.cleaned_data['narrative'],
            enrolment_id=self.enrolment.id,
            type_id=form.cleaned_data['type'].id,
        )
        return super().form_valid(form)

    def get_success_url(self):
        if url_has_allowed_host_and_scheme(self.request.GET.get('next'), allowed_hosts=None):
            return self.request.GET['next']
        return self.enrolment.get_absolute_url()


class AddModuleFees(LoginRequiredMixin, generic.View):
    """POST endpoint for AddFees' table.  Can add multiple fees to an enrolment"""

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        enrolment = get_object_or_404(Enrolment, pk=self.kwargs['enrolment_id'])
        fee_ids = request.POST.getlist('fee')
        fees = Fee.objects.filter(id__in=fee_ids, module_id=enrolment.module_id)
        if not fees:
            messages.error(request, 'You must select a fee')
            return redirect(reverse('finance:add-fees', args=[enrolment.pk]))

        for fee in fees:
            services.add_enrolment_fee(enrolment_id=enrolment.id, fee_id=fee.id, user=request.user)
        messages.success(request, f'{len(fees)} fees added')
        return redirect(enrolment.get_absolute_url())
