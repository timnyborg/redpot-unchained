from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect
from django.utils.text import slugify
from django.views import generic

from apps.core.utils.dates import academic_year
from apps.core.utils.urls import next_url_if_safe
from apps.core.utils.views import AutoTimestampMixin, ExcelExportView, PageTitleMixin
from apps.discount.models import Discount
from apps.enrolment.models import Enrolment
from apps.tutor.utils import expense_forms

from . import exports, forms, services
from .datatables import BookTable, ModuleSearchFilter, ModuleSearchTable, WaitlistTable
from .models import Module, ModuleStatus


class Clone(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, AutoTimestampMixin, generic.CreateView):
    """Allows cloning a given module.  Accessible via .../<pk> or .../?module=<pk>"""

    form_class = forms.CloneForm
    template_name = 'core/form.html'
    success_message = 'Module cloned'
    title = 'Module'
    subtitle = 'Clone'

    def get_form_kwargs(self):
        # Set the source module, and use it to determine which form fields to remove
        module_pk = self.request.GET.get('module') or self.kwargs.get('pk')
        self.src_module = get_object_or_404(Module, pk=module_pk)
        remove_fields = []
        if self.src_module.portfolio_id != 32:  # todo: consider what to do with this logic
            remove_fields.append('is_repeat')
        if not self.src_module.books.exists():
            remove_fields.append('copy_books')

        kwargs = super().get_form_kwargs()
        return {'remove_fields': remove_fields, **kwargs}

    def get_initial(self) -> dict:
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
        services.clone_fields(
            source=self.src_module,
            target=form.instance,
            copy_url=form.cleaned_data['keep_url'],
            copy_dates=form.cleaned_data['copy_dates'],
        )
        form.instance.save()
        # Which child records are copied are (partly) down to the form selections
        services.copy_children(source=self.src_module, target=form.instance, user=self.request.user)
        if form.cleaned_data.get('copy_fees'):
            services.copy_fees(source=self.src_module, target=form.instance, user=self.request.user)
        if form.cleaned_data.get('copy_books'):
            services.copy_books(source=self.src_module, target=form.instance)
        return response


class CopyFees(LoginRequiredMixin, PageTitleMixin, generic.FormView):
    form_class = forms.CopyFeesForm
    template_name = 'core/form.html'
    title = 'Module'

    def dispatch(self, request, *args, **kwargs):
        self.target_module = get_object_or_404(Module, pk=self.kwargs['module_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_subtitle(self):
        return f'Copy fees – {self.target_module.title} ({self.target_module.code})'

    def form_valid(self, form):
        source_module = form.cleaned_data['source_module']
        copied = services.copy_fees(
            source=source_module,
            target=self.target_module,
            user=self.request.user,
        )
        messages.success(self.request, f'{copied} fee(s) copied from {source_module}')
        return redirect(self.target_module.get_absolute_url() + '#fees')


class CopyWebFields(LoginRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.FormView):
    form_class = forms.CopyFieldsForm
    template_name = 'core/form.html'
    title = 'Module'

    def dispatch(self, request, *args, **kwargs):
        self.target_module = get_object_or_404(Module, pk=self.kwargs['module_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_subtitle(self):
        return f'Copy web fields – {self.target_module.title} ({self.target_module.code})'

    def form_valid(self, form):
        services.copy_web_fields(
            source=form.cleaned_data['source_module'],
            target=self.target_module,
            user=self.request.user,
        )
        self.target_module.save()
        messages.success(self.request, 'Web fields copied')
        return redirect(self.target_module.get_absolute_url())


class Edit(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, AutoTimestampMixin, generic.UpdateView):
    model = Module
    form_class = forms.EditForm
    template_name = 'core/form.html'
    success_message = 'Details updated.'


class New(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, AutoTimestampMixin, generic.CreateView):
    form_class = forms.CreateForm
    template_name = 'module/new.html'
    model = Module
    success_message = 'Module created'

    def get_context_data(self, **kwargs):
        # Add in the extra lookup form (submit to another page via GET)
        context = super().get_context_data(**kwargs)
        context['lookup_form'] = forms.LookupForm()
        return context

    def form_valid(self, form):
        # Default to the portfolio's email and phone
        form.instance.email = form.instance.portfolio.email
        form.instance.phone = form.instance.portfolio.phone
        return super().form_valid(form)


class Search(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    template_name = 'core/search.html'
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

        waitlist_table = WaitlistTable(self.object.waitlists.all(), request=self.request)
        book_table = BookTable(self.object.books.all(), request=self.request)

        discounts = Discount.objects.matching_module(self.object).with_eligibility()

        other_runs = self.object.other_runs()
        next_run = self.object.next_run()

        applications = self.object.course_applications.select_related('student')
        subjects = self.object.subjects.all()
        hecos_subjects = self.object.hecos_subjects.all()
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
            'hecos_subjects': hecos_subjects,
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

    def get_initial(self) -> dict:
        return {'module': self.module}

    def get_success_url(self) -> str:
        return next_url_if_safe(self.request) or self.module.get_absolute_url()


class StudentList(LoginRequiredMixin, ExcelExportView):
    export_class = exports.StudentListExport

    def get(self, request, *args, **kwargs):
        self.module = get_object_or_404(Module, pk=kwargs['pk'])
        return super().get(request, *args, **kwargs)

    def get_filename(self):
        return f'{self.module.code}_student_list.xlsx'

    def get_export_queryset(self):
        return Enrolment.objects.filter(module=self.module)


class MoodleList(LoginRequiredMixin, ExcelExportView):
    export_class = exports.MoodleListExport

    def get(self, request, *args, **kwargs):
        self.module = get_object_or_404(Module, pk=kwargs['pk'])
        return super().get(request, *args, **kwargs)

    def get_filename(self):
        title = slugify(self.module.title)
        return f"{self.module.code}_{title}.xlsx"

    def get_export_queryset(self):
        return Enrolment.objects.filter(
            module=self.module,
            status__in=[10, 90],  # Todo: use a column or enum
        )


class AssignMoodleIDs(LoginRequiredMixin, SuccessMessageMixin, generic.View):
    """Generates moodle IDs for all a module's students, redirecting back to the module page"""

    http_method_names = ['get']

    # todo: convert to POST once we have a good POST-link solution,
    #  or even better, that link is ajax'ed and handles message popups!
    def get(self, request, module_id: int) -> http.HttpResponse:
        module = get_object_or_404(Module, pk=module_id)
        count = services.assign_moodle_ids(module=module, created_by=request.user.username)
        messages.success(request, f'{count} moodle ID(s) generated')
        return redirect(module)


class EditHESASubjects(
    LoginRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.detail.SingleObjectMixin, generic.FormView
):
    model = Module
    form_class = forms.HESASubjectFormSet
    template_name = 'module/edit_hesa_subjects.html'
    subtitle = 'HESA subjects'
    success_message = 'Subjects updated'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {**kwargs, 'instance': self.object}

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()
