from __future__ import annotations

import csv
from datetime import date
from urllib.parse import urlencode

from dateutil.relativedelta import relativedelta
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.detail import SingleObjectMixin

from apps.core.utils.urls import next_url_if_safe
from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin
from apps.tutor.models import TutorModule

from . import datatables, forms, models, services


class Create(PermissionRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.CreateView):
    model = models.TutorPayment
    permission_required = 'tutor_payment.raise'
    template_name = 'core/form.html'
    form_class = forms.PaymentForm

    def dispatch(self, request, *args, **kwargs):
        # get the parent record for generating the title and adding to the child record on form submission
        self.tutor_module = get_object_or_404(TutorModule, pk=self.kwargs['tutor_module_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.tutor_module = self.tutor_module
        form.instance.raised_by = self.request.user
        return super().form_valid(form)

    def get_subtitle(self):
        return f'New – {self.tutor_module}'

    def get_success_url(self) -> str:
        return next_url_if_safe(self.request) or self.tutor_module.get_absolute_url() + '#payments'


class Edit(LoginRequiredMixin, SuccessMessageMixin, PageTitleMixin, AutoTimestampMixin, generic.UpdateView):
    model = models.TutorPayment
    form_class = forms.PaymentForm
    success_message = 'Record updated'
    template_name = 'core/form.html'
    subtitle_object = False

    def get_form_kwargs(self):
        # If not allowed to edit, display instead. should this be elsewhere?
        if not self.object.user_can_edit(self.request.user):
            return redirect(self.object.get_absolute_url())

        kwargs = super().get_form_kwargs()
        kwargs['editable_status'] = self.request.user.has_perm('tutor_payment.transfer')
        return kwargs

    def get_success_url(self) -> str:
        return next_url_if_safe(self.request) or self.object.tutor_module.get_absolute_url() + '#payments'


class Delete(PermissionRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = models.TutorPayment
    template_name = 'core/delete_form.html'
    success_url = reverse_lazy('tutor-payment:search')
    subtitle = 'Delete'
    subtitle_object = False

    def has_permission(self) -> bool:
        return self.get_object().user_can_edit(self.request.user)


class Search(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    title = 'Tutor payment'
    subtitle = 'Search'
    template_name = 'core/search.html'

    table_class = datatables.SearchTable
    filterset_class = datatables.SearchFilter


class Approve(PermissionRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    """List of payments assigned to the current user"""

    model = models.TutorPayment
    permission_required = 'tutor_payment.approve'
    template_name = 'tutor_payment/approve.html'
    subtitle = 'Approve'

    table_class = datatables.ApprovalTable
    filterset_class = datatables.ApprovalFilter

    def get_queryset(self) -> QuerySet:
        return self.request.user.approver_payments.filter(status=models.Statuses.RAISED).select_related(
            'type', 'tutor_module__tutor__student', 'tutor_module__module'
        )

    def post(self, request, urllib=None, *args, **kwargs) -> http.HttpResponse:
        ids: list[str] = request.POST.getlist('payment')
        int_ids: list[int] = [int(i) for i in ids if i.isnumeric()]
        update_count = services.approve_payments(payment_ids=int_ids, username=request.user.username)
        message_method = messages.success if update_count else messages.error
        message_method(request, f"{update_count or 'No'} payments approved")
        return redirect(self.request.path_info + '?' + urlencode(self.request.GET))  # preserve filtering


class Extras(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, SingleObjectMixin, generic.FormView):
    template_name = 'tutor_payment/extras.html'
    form_class = forms.ExtrasForm
    model = TutorModule
    title = 'Tutor Payment'
    subtitle = 'Extras'
    success_message = 'Payments added'

    def dispatch(self, request, *args, **kwargs):
        # Set object so we can use it in several places
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return self.object.get_absolute_url() + '#payments'

    def form_valid(self, form):
        form.create_record(
            tutor_module=self.object,
            user=self.request.user,
        )
        return super().form_valid(form)


class OnlineTeaching(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, SingleObjectMixin, generic.FormView):
    model = TutorModule
    template_name = 'core/form.html'
    success_message = 'Fees added'
    form_class = forms.OnlineTeachingForm
    title = 'Tutor payment'
    subtitle = 'Teaching'

    def dispatch(self, request, *args, **kwargs) -> http.HttpResponse:
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form) -> http.HttpResponse:
        # All variations of the form include the schedule field
        services.create_teaching_fee(
            tutor_module=self.object,
            amount=form.cleaned_data['amount'].amount,
            rate=models.PaymentRate.objects.lookup('online_hourly_rate'),
            schedule=form.cleaned_data['schedule'],
            approver=form.cleaned_data['approver'],
            raised_by=self.request.user,
        )
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()


class WeeklyTeaching(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, SingleObjectMixin, generic.FormView):
    model = TutorModule
    template_name = 'core/form.html'
    success_message = 'Fees added'
    form_class = forms.WeeklyTeachingForm
    title = 'Tutor payment'
    subtitle = 'Teaching'

    def dispatch(self, request, *args, **kwargs) -> http.HttpResponse:
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self) -> dict:
        return {
            'rate': models.PaymentRate.objects.lookup('weekly_hourly_rate'),
            'no_meetings': self.object.module.no_meetings,
        }

    def form_valid(self, form) -> http.HttpResponse:
        services.create_teaching_fee(
            tutor_module=self.object,
            amount=form.cleaned_data['length'] * form.cleaned_data['rate'] * form.cleaned_data['no_meetings'],
            rate=form.cleaned_data['rate'],
            schedule=form.cleaned_data['schedule'],
            approver=form.cleaned_data['approver'],
            raised_by=self.request.user,
        )
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()


class AddSyllabusFee(LoginRequiredMixin, generic.View):
    """Adds a syllabus prep fee for a weekly class"""

    def post(self, request, *args, **kwargs) -> http.HttpResponse:  # todo: post
        tutor_module = get_object_or_404(TutorModule, **self.kwargs)

        if not request.user.default_approver:
            messages.error(request, 'Cannot add syllabus fees: no default approver set in your user profile')
            return redirect(tutor_module)

        # To be paid (with holiday) the month after starting
        start_date = tutor_module.module.start_date
        if not start_date:
            messages.error(request, 'Cannot add syllabus fees: module needs a start date')
            return redirect(tutor_module)

        pay_date = date(start_date.year, start_date.month, 1) + relativedelta(months=1)

        rate = models.PaymentRate.objects.lookup('weekly_hourly_rate')
        amount = 3 * rate

        models.TutorPayment.create_with_holiday(
            tutor_module=tutor_module,
            amount=amount,
            payment_type_id=models.Types.TEACHING,
            details=f'Syllabus prep fee (£{amount:.2f})',
            approver=request.user.default_approver,
            hourly_rate=rate,
            weeks=1,
            raised_by=request.user,
            pay_date=pay_date,
            holiday_date=pay_date,
        )

        messages.success(request, f'Syllabus fee added (£{amount:.2f})')
        return redirect(tutor_module.get_absolute_url() + '#payments')


class Export(PermissionRequiredMixin, generic.View):
    """Produces a CSV of a batch of payments"""

    permission_required = 'tutor_payment.transfer'

    columns = {
        'surname': 'Surname',
        'initial': 'Initial',
        'employee_no': 'Employee number',
        'appointment_id': 'Appointment ID',
        'limited_hours': 'Hours limited by visa?',
        'week_ending': 'Week/period ending',
        'pay_code': 'Pay code',
        'cash_value': 'Cash value',
        'hours_value': 'Hours value',
        'hourly_rate': 'Rate of pay',
        'cost_centre': 'Cost centre',
        'project': 'Project',
        'comment': 'Comment',
        'batch': 'Batch',
        'weeks': 'Weeks',
    }

    def get(self, request, batch: int, *args, **kwargs) -> http.HttpResponse:
        response = http.HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="tutor_payment_batch_{batch}.csv"'},
        )
        writer = csv.DictWriter(response, fieldnames=self.columns)
        writer.writerow(self.columns)
        for row in self.get_csv_rows(batch):
            writer.writerow(row)
        return response

    @staticmethod
    def get_csv_rows(batch: int) -> list[dict]:
        payments = (
            models.TutorPayment.objects.filter(batch=batch).select_related(
                'type',
                'tutor_module__module',
                'tutor_module__tutor',
                'tutor_module__tutor__student',
                'tutor_module__tutor__rtw_document_type',
            )
            # Keep casual and main payroll as groups, and individuals grouped together
            .order_by('tutor_module__tutor__appointment_id')
        )

        fees = []

        for payment in payments:
            module = payment.tutor_module.module
            tutor = payment.tutor_module.tutor

            common = {
                'surname': tutor.student.surname,
                'initial': tutor.student.firstname[0],
                'employee_no': tutor.employee_no,
                'appointment_id': tutor.appointment_id,
                'limited_hours': 'Yes' if tutor.rtw_document_type and tutor.rtw_document_type.limited_hours else 'No',
                'week_ending': '',
                'pay_code': payment.type.code,
                'cost_centre': f'{module.cost_centre}00{module.source_of_funds}' if module.finance_code else '',
                'project': '',
                'comment': '',
                'batch': payment.batch,
                'weeks': payment.weeks,
            }

            if tutor.is_casual:
                # Casual payroll needs to be split by week
                for _ in range(payment.weeks):  # Create a row for every week
                    fees.append(
                        {
                            # Divided per week
                            'cash_value': payment.amount / payment.weeks if not payment.hours_worked else '',
                            'hours_value': payment.hours_worked / payment.weeks if payment.hours_worked else '',
                            'hourly_rate': payment.hourly_rate,
                            **common,
                        }
                    )
            else:
                # Main payroll has a single payment.
                # A function might be in order which takes 'divide_weeks=False'
                fees.append(
                    {
                        'cash_value': payment.amount if not payment.hours_worked else '',  # Full amount
                        'hours_value': payment.hours_worked or '',  # Full amount
                        'hourly_rate': payment.hourly_rate,
                        **common,
                    }
                )
        return fees
