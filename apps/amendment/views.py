from __future__ import annotations

from datetime import datetime
from typing import Type

import django_tables2 as tables
from django_filters.views import FilterView

from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from apps.core.utils.urls import next_url_if_safe
from apps.core.utils.views import PageTitleMixin
from apps.enrolment.models import Enrolment

from . import datatables, forms, models, services

FORM_CLASSES: dict[int, Type[ModelForm]] = {
    models.AmendmentTypes.TRANSFER: forms.TransferForm,
    models.AmendmentTypes.AMENDMENT: forms.AmendmentForm,
    models.AmendmentTypes.ONLINE_REFUND: forms.RefundForm,
    models.AmendmentTypes.CREDIT_CARD_REFUND: forms.RefundForm,
    models.AmendmentTypes.RCP_REFUND: forms.RefundForm,
    models.AmendmentTypes.BANK_REFUND: forms.RefundForm,
}


class Create(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, generic.CreateView):
    model = models.Amendment
    success_message = 'Request submitted for approval'
    template_name = 'core/form.html'

    def dispatch(self, request, *args, **kwargs) -> http.HttpResponse:
        self.enrolment = get_object_or_404(Enrolment, pk=self.kwargs['enrolment_id'])
        self.amendment_type = get_object_or_404(models.AmendmentType, pk=self.kwargs['type_id'])

        if self.amendment_type == models.AmendmentTypes.OTHER_REFUND:
            # Refunds requiring paper forms (BACS?) # Todo - handle this elsewhere - service?  Standalone view?
            amendment = models.Amendment.objects.create(
                details='See printed form for details',
                status_id=models.AmendmentStatuses.APPROVED,
                requested_by=request.user.username,
                requested_on=datetime.now(),
                approved_by=request.user.username,
                approved_on=datetime.now(),
            )
            amendment.narrative = services.get_narrative(amendment=amendment)
            amendment.save()
            return redirect(settings.STATIC_URL + 'templates/bacs_refund_form_r12.xls')
        return super().dispatch(request, *args, **kwargs)

    def get_subtitle(self) -> str:
        return f'New – {self.enrolment.qa.student} on {self.enrolment.module}'

    def get_form_class(self) -> Type[ModelForm]:
        return FORM_CLASSES[self.amendment_type.id]

    def get_initial(self) -> dict:
        return {
            'type': self.amendment_type,
            'enrolment': self.enrolment,
        }

    def form_valid(self, form) -> http.HttpResponse:
        form.instance.requested_on = datetime.now()
        form.instance.requested_by = self.request.user
        form.instance.narrative = services.get_narrative(amendment=form.instance)
        services.send_request_created_email(amendment=form.instance)
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.enrolment.get_absolute_url() + '#finances'


class Edit(PermissionRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.UpdateView):
    model = models.Amendment
    template_name = 'amendment/edit.html'
    permission_denied_message = 'You do not have permission to edit this change request'
    success_message = 'Change request updated'

    def has_permission(self) -> bool:
        return services.user_can_edit(user=self.request.user, amendment=self.get_object())

    def get_subtitle(self) -> str:
        return f'Edit – {self.object.enrolment.qa.student} on {self.object.enrolment.module}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_apply_refund'] = self.object.can_apply_refund and self.request.user.has_perm(
            'amendment.edit_finance'
        )
        return context

    def get_form_class(self) -> Type[ModelForm]:
        return FORM_CLASSES[self.object.type_id]

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        edit_finance_fields = self.request.user.has_perm('amendment.edit_finance')
        return {**kwargs, 'edit_finance_fields': edit_finance_fields}

    def get_success_url(self) -> str:
        return next_url_if_safe(self.request) or self.object.enrolment.get_absolute_url() + '#finances'

    def form_valid(self, form) -> http.HttpResponse:
        if not form.cleaned_data.get('narrative'):
            # Update narrative if it wasn't part of the form submission
            form.instance.narrative = services.get_narrative(amendment=form.instance)

        if form.instance.is_complete:
            form.instance.status_id = models.AmendmentStatuses.COMPLETE
            form.instance.executed_by = self.request.user.username
            form.instance.executed_on = datetime.now()
            services.send_request_complete_email(amendment=form.instance)
            self.success_message = 'Change request complete'
        return super().form_valid(form)


class Delete(PermissionRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = models.Amendment
    template_name = 'core/delete_form.html'
    permission_denied_message = 'You do not have permission to edit this amendment'

    def has_permission(self) -> bool:
        return services.user_can_edit(user=self.request.user, amendment=self.get_object())

    def get_subtitle(self) -> str:
        return f'Delete – {self.object.enrolment.qa.student} on {self.object.enrolment.module}'

    def get_success_url(self) -> str:
        messages.success(self.request, 'Change request cancelled')
        # todo: put notification email here (or in def delete) if still useful (_email_request_cancellation)
        return self.object.enrolment.get_absolute_url() + '#finances'


class Approve(PermissionRequiredMixin, PageTitleMixin, tables.SingleTableView):
    """List of amendments assigned to the current user"""

    model = models.Amendment
    permission_required = 'amendment.approve'
    table_class = datatables.ApprovalTable
    template_name = 'amendment/approve.html'
    subtitle = 'Approve'

    def get_queryset(self) -> QuerySet:
        return self.request.user.approver_change_requests.filter(
            status=models.AmendmentStatuses.RAISED
        ).select_related('enrolment__qa__student', 'enrolment__module', 'requested_by', 'type')

    def post(self, request, *args, **kwargs) -> http.HttpResponse:
        ids: list[str] = request.POST.getlist('amendment')
        int_ids: list[int] = [int(i) for i in ids if i.isnumeric()]
        update_count = services.approve_amendments(amendment_ids=int_ids, username=request.user.username)
        if update_count:
            messages.success(request, f'{update_count} requests approved')
        else:
            messages.error(request, 'No requests approved')
        return redirect(self.request.path_info)


class Search(LoginRequiredMixin, PageTitleMixin, tables.SingleTableMixin, FilterView):
    """Filterable list of change requests"""

    queryset = models.Amendment.objects.select_related('type', 'status', 'requested_by')
    table_class = datatables.SearchTable
    filterset_class = datatables.SearchFilter
    template_name = 'core/search.html'
    subtitle = 'Search'


class ApplyOnlineRefund(PermissionRequiredMixin, generic.View):
    """Automatically creates fee lines for an online refund"""

    permission_required = 'amendment.edit_finance'

    def post(self, request, pk, *args, **kwargs):
        amendment = get_object_or_404(models.Amendment, pk=pk)
        services.apply_online_refund(amendment=amendment, user=request.user)
        messages.success(request, 'Refund applied')
        return redirect(next_url_if_safe(request) or amendment.enrolment.get_absolute_url() + '#finances')
