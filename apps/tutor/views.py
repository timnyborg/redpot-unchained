import os
import pathlib

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import FilteredRelation, Q, QuerySet
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from apps.core.utils.mail_merge import MailMergeView
from apps.core.utils.urls import next_url_if_safe
from apps.core.utils.views import AutoTimestampMixin, DeletionFailedMessageMixin, PageTitleMixin
from apps.module.models import Module

from . import forms, services
from .models import Tutor, TutorActivity, TutorModule


class Edit(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, AutoTimestampMixin, generic.UpdateView):
    model = Tutor
    template_name = 'core/form.html'
    success_message = 'Tutor details updated'

    def get_form_class(self):
        # Show a full or reduced form depending on the user's rights
        if self.request.user.has_perm('tutor.edit_bank_details'):
            return forms.Edit
        return forms.BasicEdit

    def form_valid(self, form) -> http.HttpResponse:
        services.email_personnel_change(
            model=self.object, initial_values=form.initial, changed_data=form.changed_data, user=self.request.user
        )
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url() + '#tutor'


class RightToWork(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, AutoTimestampMixin, generic.UpdateView):
    model = Tutor
    template_name = 'tutor/rtw_form.html'
    form_class = forms.RightToWork
    subtitle = 'Right to work'
    success_message = 'Right to work details updated'

    def get_initial(self) -> dict:
        if not self.object.rtw_check_by:
            return {'rtw_check_by': self.request.user.get_full_name()}
        return {}


class TutorOnModuleView(PageTitleMixin, LoginRequiredMixin, generic.DetailView):
    model = TutorModule
    template_name = 'tutor_module/view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        payments = self.object.payments.order_by('id')

        add_buttons = []
        if self.object.module.portfolio_id == 17:  # Online
            add_buttons = ['online_teaching', 'marking_link']
        elif self.object.module.portfolio_id == 32:
            add_buttons = ['weekly_teaching', 'marking_link', 'weekly_syllabus']

        return {
            'payments': payments,
            'add_buttons': add_buttons,
            **context,
        }


class TutorOnModuleEdit(
    PageTitleMixin, SuccessMessageMixin, AutoTimestampMixin, LoginRequiredMixin, generic.UpdateView
):
    model = TutorModule
    form_class = forms.TutorModuleEditForm
    template_name = 'core/form.html'
    success_message = 'Tutor-on-module record updated'

    def get_success_url(self) -> str:
        return next_url_if_safe(self.request) or self.object.get_absolute_url()


class TutorOnModuleCreate(
    PageTitleMixin, SuccessMessageMixin, AutoTimestampMixin, LoginRequiredMixin, generic.CreateView
):
    model = TutorModule
    form_class = forms.TutorModuleCreateForm
    template_name = 'core/form.html'
    success_message = 'Tutor added'

    def get_initial(self) -> dict:
        module_id = self.request.GET.get('module')
        tutor_id = self.request.GET.get('tutor')
        if module_id:
            self.module = get_object_or_404(Module, pk=module_id)
            return {'module': self.module}
        elif tutor_id:
            self.tutor = get_object_or_404(Tutor, pk=tutor_id)
            return {'tutor': self.tutor}
        raise http.Http404('Requires a module or tutor')

    def get_success_url(self) -> str:
        return next_url_if_safe(self.request) or self.object.module.get_absolute_url() + '#tutor-modules'


class TutorOnModuleDelete(PageTitleMixin, DeletionFailedMessageMixin, LoginRequiredMixin, generic.DeleteView):
    model = TutorModule
    template_name = 'core/delete_form.html'

    def get_success_url(self) -> str:
        return next_url_if_safe(self.request) or self.object.module.get_absolute_url() + '#tutor-modules'

    def on_success(self) -> http.HttpResponse:
        messages.success(self.request, f'{self.object.tutor} removed from module {self.object.module}')
        return super().on_success()

    def on_failure(self, request, *args, **kwargs) -> http.HttpResponse:
        if 'next' in request.GET:
            return redirect(next_url_if_safe(request))
        return super().on_failure(request, *args, **kwargs)


class ExpenseFormView(MailMergeView):
    def get_filename(self, queryset) -> str:
        record = queryset[0]
        if self.kwargs['mode'] == 'module':
            return f'{record.module.code}_expense_forms.docx'
        elif self.kwargs['mode'] == 'single':
            return (
                f'{record.tutor.student.firstname}_{record.tutor.student.surname}'
                f'_{record.module.code}_expense_form.docx'.replace(' ', '_')
            )
        else:
            return 'batch_expense_form.docx'

    def get_template_file(self, queryset) -> str:
        return os.path.join(
            pathlib.Path(__file__).parent.absolute(),
            'templates/tutor_expense_forms',
            self.kwargs['template'] + '.docx',
        )

    def get_queryset(self) -> QuerySet:
        # select_related on a FilteredRelation lets us bring in the default address very easily
        queryset = TutorModule.objects.annotate(
            address=FilteredRelation('tutor__student__address', condition=Q(tutor__student__address__is_default=True))
        ).select_related('address', 'module', 'tutor__student')

        if self.kwargs['mode'] == 'module':
            return queryset.filter(module=self.kwargs['pk'])
        elif self.kwargs['mode'] == 'single':
            return queryset.filter(pk=self.kwargs['pk'])
        elif self.kwargs['mode'] == 'search':
            # Wildcard based matching
            return queryset.filter(module__code__like=self.kwargs['search'])

    def get_merge_data(self) -> list:
        return [
            {
                'tutor_name': f'{record.tutor.student.firstname} {record.tutor.student.surname}'.strip(),
                'nickname': record.tutor.student.nickname,
                'birthdate': (
                    record.tutor.student.birthdate.strftime('%d %b %Y') if record.tutor.student.birthdate else ''
                ),
                'gender': record.tutor.student.gender,
                'line1': record.address.line1 if hasattr(record, 'address') else '',
                'line2': record.address.line2 if hasattr(record, 'address') else '',
                'line3': record.address.line3 if hasattr(record, 'address') else '',
                'town': record.address.town if hasattr(record, 'address') else '',
                'county_state': record.address.countystate if hasattr(record, 'address') else '',
                'country': record.address.country if hasattr(record, 'address') else '',
                'postcode': record.address.postcode if hasattr(record, 'address') else '',
                'bankname': record.tutor.bankname,
                'branchaddress': record.tutor.branchaddress,
                'sortcode': record.tutor.sortcode,
                'accountno': record.tutor.accountno,
                'accountname': record.tutor.accountname,
                'iban': record.tutor.iban,
                'swift': record.tutor.swift,
                'nino': record.tutor.nino or record.tutor.student.nationality.name,
                'appointment_id': record.tutor.appointment_id,
                'employee_no': record.tutor.employee_no,
                'title': record.module.title,
                'code': record.module.code,
                'start_date': record.module.start_date.strftime('%d %B %y') if record.module.start_date else '',
                'end_date': record.module.end_date.strftime('%d %B %y') if record.module.end_date else '',
                'accredited': '□' if record.module.non_credit_bearing else 'X',
                'cost_centre': record.module.cost_centre,
                'activity': record.module.activity_code,
                'source_of_funds': record.module.source_of_funds,
            }
            for record in self.queryset.all()[:20]  # todo: remove limit once docx-mailmerge updated
        ]


class CreateTutorActivity(
    LoginRequiredMixin, AutoTimestampMixin, PageTitleMixin, SuccessMessageMixin, generic.CreateView
):
    form_class = forms.TutorActivityForm
    template_name = 'core/form.html'
    model = TutorActivity
    success_message = 'Activity added'

    def get_initial(self) -> dict:
        return {'tutor': get_object_or_404(Tutor, pk=self.kwargs['tutor_id'])}


class EditTutorActivity(
    LoginRequiredMixin, AutoTimestampMixin, PageTitleMixin, SuccessMessageMixin, generic.UpdateView
):
    form_class = forms.TutorActivityForm
    template_name = 'core/form.html'
    model = TutorActivity
    success_message = 'Activity updated'
    subtitle_object = None


class DeleteTutorActivity(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = TutorActivity
    template_name = 'core/delete_form.html'
    subtitle_object = None

    def get_success_url(self) -> str:
        messages.success(self.request, 'Activity deleted')
        return self.object.get_absolute_url()
