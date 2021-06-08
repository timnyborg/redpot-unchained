from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from apps.core.utils.dates import academic_year
from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin
from apps.discount.models import Discount
from apps.tutor.utils import expense_forms

from . import forms
from .datatables import BookTable, ModuleSearchFilter, ModuleSearchTable, WaitlistTable
from .models import Module, ModuleStatus
from .services import clone_fields, copy_books, copy_children, copy_fees


class Clone(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, AutoTimestampMixin, generic.CreateView):
    form_class = forms.CloneForm
    template_name = 'module/clone.html'
    success_message = 'Module cloned'
    title = 'Module'
    subtitle = 'Clone'

    def get_form_kwargs(self):
        # Set the source module, and use it to determine which form fields to remove
        self.src_module = get_object_or_404(Module, pk=self.kwargs['pk'])
        remove_fields = []
        if self.src_module.portfolio_id != 32:  # todo: consider what to do with this logic
            remove_fields.append('is_repeat')
        if not self.src_module.books.exists():
            remove_fields.append('copy_books')

        kwargs = super().get_form_kwargs()
        return {'remove_fields': remove_fields, **kwargs}

    def get_initial(self):
        initial = super().get_initial()
        # Increment the default ID to the next academic year
        new_code = self.src_module.code[:1] + str(academic_year() + 1)[2:] + self.src_module.code[3:]
        return {
            **initial,
            'source_module': self.src_module.long_form,
            'title': self.src_module.title,
            'code': new_code,
            'is_repeat': False,
        }

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.source_module_code = self.src_module.code
        clone_fields(
            source=self.src_module,
            target=form.instance,
            copy_url=form.cleaned_data['keep_url'],
            copy_dates=form.cleaned_data['copy_dates'],
        )
        form.instance.save()
        # Which child records are copied are (partly) down to the form selections
        copy_children(source=self.src_module, target=form.instance, user=self.request.user)
        if form.cleaned_data.get('copy_fees'):
            copy_fees(source=self.src_module, target=form.instance, user=self.request.user)
        if form.cleaned_data.get('copy_books'):
            copy_books(source=self.src_module, target=form.instance)
        return response


class Edit(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, AutoTimestampMixin, generic.UpdateView):
    model = Module
    form_class = forms.EditForm
    template_name = 'module/edit.html'
    success_message = 'Details updated.'


class New(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, AutoTimestampMixin, generic.CreateView):
    form_class = forms.CreateForm
    template_name = 'module/new.html'
    model = Module
    subtitle_object = False
    success_message = 'Module created'

    def form_valid(self, form):
        # Default to the portfolio's email and phone
        form.instance.email = form.instance.portfolio.email
        form.instance.phone = form.instance.portfolio.phone
        return super().form_valid(form)


class Search(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    template_name = 'module/search.html'
    queryset = Module.objects.select_related('division', 'portfolio')
    table_class = ModuleSearchTable
    filterset_class = ModuleSearchFilter
    subtitle = 'Search'


class View(LoginRequiredMixin, PageTitleMixin, generic.DetailView):
    queryset = Module.objects.defer(None)  # Get all fields
    template_name = 'module/view.html'

    def get_subtitle(self):
        return f'View – {self.object.title} ({self.object.code})'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        enrolments = self.object.enrolments.select_related('result', 'status', 'qa__student').order_by(
            'qa__student__surname', 'qa__student__firstname'
        )

        fees = self.object.fees.order_by('-type__display_order', 'description').select_related('type').all()
        programmes = self.object.programmes.order_by('title').select_related('qualification').all()

        tutors = self.object.tutor_modules.select_related('tutor__student').order_by(
            Coalesce('display_order', 999), 'id'
        )

        expense_form_options = expense_forms.template_options(self.object)

        waitlist_table = WaitlistTable(self.object.waitlist.all())
        book_table = BookTable(self.object.books.all())

        discounts = Discount.objects.matching_module(self.object).with_eligibility()

        other_runs = self.object.other_runs()
        next_run = self.object.next_run()

        applications = self.object.applications.select_related('student')
        subjects = self.object.subjects.all()
        payment_plans = self.object.payment_plans.all()
        marketing_types = self.object.marketing_types.all()

        statuses = ModuleStatus.objects.all()

        return {
            'enrolments': enrolments,
            'fees': fees,
            'programmes': programmes,
            'tutors': tutors,
            'expense_form_options': expense_form_options,
            'waitlist_table': waitlist_table,
            'payment_plans': payment_plans,
            'book_table': book_table,
            'other_runs': other_runs,
            'next_run': next_run,
            'discounts': discounts,
            'statuses': statuses,
            'applications': applications,
            'subjects': subjects,
            'marketing_types': marketing_types,
            **context,
        }


class AddProgramme(LoginRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.CreateView):
    template_name = 'core/form.html'
    form_class = forms.AddProgrammeForm
    success_message = 'Module attached'
    title = 'Module'
    subtitle = 'Attach to programme'

    def dispatch(self, request, *args, **kwargs):
        self.module = get_object_or_404(Module, pk=kwargs['module_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.module = self.module
        return super().form_valid(form)

    def get_success_url(self):
        if url_has_allowed_host_and_scheme(self.request.GET.get('next'), allowed_hosts=None):
            return self.request.GET.get('next')
        return self.module.get_absolute_url()


@login_required
@csrf_exempt
def toggle_auto_reminder(request, pk):
    obj = Module.objects.get(id=pk)
    obj.auto_reminder = not obj.auto_reminder
    obj.save()
    return HttpResponse()


@login_required
@csrf_exempt
def toggle_auto_feedback(request, pk):
    obj = Module.objects.get(id=pk)
    obj.auto_feedback = not obj.auto_feedback
    obj.save()
    return HttpResponse()
