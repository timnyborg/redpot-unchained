from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

import apps.student.services as student_services
from apps.core.utils.views import AutoTimestampMixin, DeletionFailedMessageMixin, PageTitleMixin
from apps.finance.models import Ledger, TransactionTypes
from apps.qualification_aim.models import QualificationAim

from . import datatables, forms, models, services


class Create(LoginRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.FormView):
    """Enrol a student on a module, while supplementing any missing student data required by HESA"""

    form_class = forms.CreateForm
    template_name = 'core/form.html'
    title = 'Enrolment'
    success_message = 'Enrolment created'

    def dispatch(self, request, *args, **kwargs):
        self.qa = get_object_or_404(QualificationAim, pk=self.kwargs['qa_id'])
        self.missing_student_fields = student_services.missing_student_data(student=self.qa.student)
        return super().dispatch(request, *args, **kwargs)

    def get_subtitle(self):
        return f'Create – {self.qa.student} – {self.qa.title}'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {
            **kwargs,
            'qa': self.qa,
            'limit_modules': not self.request.GET.get('all'),
            'missing_student_fields': self.missing_student_fields,
        }

    def get_initial(self):
        return {
            'qa': self.qa,
            'status': models.Statuses.PROVISIONAL,
        }

    def form_valid(self, form):
        self.enrolment = services.create_enrolment(
            qa=self.qa,
            module=form.cleaned_data['module'],
            status=form.cleaned_data['status'],
            user=self.request.user,
        )
        if self.missing_student_fields:
            supplement_data = {field: form.cleaned_data[field] for field in self.missing_student_fields}
            student_services.supplement_student_data(
                student=self.qa.student,
                **supplement_data,
            )
        return super().form_valid(form)

    def get_success_url(self):
        # Weekly classes redirect to a syllabus for printing
        # todo: replace with a portfolio flag
        module = self.enrolment.module
        if module.portfolio == 32:
            querystring = urlencode({'next': self.enrolment.get_absolute_url()})
            return reverse('module:syllabus', args=[module.id]) + f'?{querystring}'
        return self.enrolment.get_absolute_url()


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

    def has_payment_of_type(self, trans_type: int) -> bool:
        """Checks whether any of the enrolment's payments match a given type, for determining amendment options"""
        return any(item.type_id == trans_type for item in self.object.ledger_set.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['finance_table'] = datatables.FinanceTable(
            data=self.object.ledger_set.debts().select_related('invoice_ledger__invoice'),
            display_finance_columns=self.request.user.has_perm('finance'),  # todo: real permission
            prefix='finances-',
            request=self.request,
        )
        context['student'] = self.object.qa.student  # for brevity in template
        context['catering'] = self.object.catering.select_related('fee')
        context['accommodation'] = self.object.accommodation.select_related('limit')
        # Determine which amendments are possible, given the financial history of the enrolment
        amendment_options = {
            'online': self.has_payment_of_type(TransactionTypes.ONLINE),
            'credit_card': self.has_payment_of_type(TransactionTypes.CREDIT_CARD),
            'rcp': self.has_payment_of_type(TransactionTypes.RCP),
        }
        context['amendment_table'] = datatables.AmendmentTable(
            data=self.object.amendments.filter(is_complete=False)
            .select_related('type', 'status')
            .order_by('status', 'requested_on'),
            prefix='amendments-',
            request=self.request,
        )
        amendment_options['any'] = any(amendment_options.values())
        context['amendment_options'] = amendment_options
        context['payment_disabled'] = not self.object.ledger_set.cash().uninvoiced().exists()
        return context


class Edit(LoginRequiredMixin, PageTitleMixin, AutoTimestampMixin, generic.UpdateView):
    model = models.Enrolment
    template_name = 'core/form.html'
    form_class = forms.EditForm

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        edit_mark = self.request.user.has_perm('enrolment.edit_mark')
        return {**kwargs, 'edit_mark': edit_mark}

    def form_valid(self, form):
        # Update module, in case it is now full/not-full
        form.instance.module.update_status()
        return super().form_valid(form)


class Delete(LoginRequiredMixin, PageTitleMixin, DeletionFailedMessageMixin, generic.DeleteView):
    model = models.Enrolment
    template_name = 'core/delete_form.html'
    success_message = 'Enrolment deleted'

    def on_success(self):
        messages.success(self.request, self.success_message)  # DeleteViews don't do this automatically
        return super().on_success()

    def get_success_url(self) -> str:
        return self.object.qa.get_absolute_url()
