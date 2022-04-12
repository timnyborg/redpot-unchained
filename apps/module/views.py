import pathlib

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import FilteredRelation, Q, QuerySet
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect
from django.utils.text import slugify
from django.views import generic

from apps.core.utils.dates import academic_year
from apps.core.utils.mail_merge import MailMergeView
from apps.core.utils.urls import next_url_if_safe
from apps.core.utils.views import AutoTimestampMixin, ExcelExportView, PageTitleMixin
from apps.discount.models import Discount
from apps.enrolment.models import CONFIRMED_STATUSES, Enrolment
from apps.fee.models import FeeTypes
from apps.invoice.models import ModulePaymentPlan
from apps.tutor.utils import expense_forms
from apps.tutor_payment.models import Statuses as PaymentStatuses
from apps.tutor_payment.models import TutorPayment

from . import datatables, exports, forms, models, services


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
        self.src_module = get_object_or_404(models.Module, pk=module_pk)
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
        self.target_module = get_object_or_404(models.Module, pk=self.kwargs['module_id'])
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
        self.target_module = get_object_or_404(models.Module, pk=self.kwargs['module_id'])
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
    model = models.Module
    form_class = forms.EditForm
    template_name = 'module/form.html'
    success_message = 'Details updated.'

    def form_valid(self, form) -> http.HttpResponse:
        # Check publication rules after saving
        response = super().form_valid(form)
        self.object.update_status()
        return response


class New(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, AutoTimestampMixin, generic.CreateView):
    form_class = forms.CreateForm
    template_name = 'module/new.html'
    model = models.Module
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
    queryset = models.Module.objects.select_related('division', 'portfolio')
    table_class = datatables.ModuleSearchTable
    filterset_class = datatables.ModuleSearchFilter
    subtitle = 'Search'


class View(LoginRequiredMixin, PageTitleMixin, generic.DetailView):
    queryset = models.Module.objects.defer(None).select_related(  # defer(None) to get all fields
        'portfolio', 'division', 'format', 'location', 'room', 'status'
    )
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

        tutors = (
            self.object.tutor_modules.select_related('tutor__student')
            .prefetch_related('contracts')
            .order_by(Coalesce('display_order', 999), 'id')
        )

        expense_form_options = expense_forms.template_options(self.object)

        waitlist_table = datatables.WaitlistTable(self.object.waitlists.all(), request=self.request)
        book_table = datatables.BookTable(self.object.books.all(), request=self.request)

        discounts = Discount.objects.matching_module(self.object)

        other_runs = self.object.other_runs()
        next_run = self.object.next_run()

        applications = self.object.applications.select_related('student')
        subjects = self.object.subjects.all()
        hecos_subjects = self.object.hecos_subjects.all()
        payment_plans = self.object.payment_plans.all()
        marketing_types = self.object.marketing_types.all()

        statuses = models.ModuleStatus.objects.all()

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
        self.module = get_object_or_404(models.Module, pk=kwargs['module_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self) -> dict:
        return {'module': self.module}

    def get_success_url(self) -> str:
        return next_url_if_safe(self.request) or self.module.get_absolute_url()


class StudentList(LoginRequiredMixin, ExcelExportView):
    export_class = exports.StudentListExport

    def get(self, request, *args, **kwargs):
        self.module = get_object_or_404(models.Module, pk=kwargs['pk'])
        return super().get(request, *args, **kwargs)

    def get_filename(self):
        return f'{self.module.code}_student_list.xlsx'

    def get_export_queryset(self):
        return Enrolment.objects.filter(module=self.module)


class MoodleList(LoginRequiredMixin, ExcelExportView):
    export_class = exports.MoodleListExport

    def get(self, request, *args, **kwargs):
        self.module = get_object_or_404(models.Module, pk=kwargs['pk'])
        return super().get(request, *args, **kwargs)

    def get_filename(self):
        title = slugify(self.module.title)
        return f"{self.module.code}_{title}.xlsx"

    def get_export_queryset(self):
        return Enrolment.objects.filter(
            module=self.module,
            status__in=CONFIRMED_STATUSES,
        )


class AssignMoodleIDs(LoginRequiredMixin, SuccessMessageMixin, generic.View):
    """Generates moodle IDs for all a module's students, redirecting back to the module page"""

    # todo: convert to POST once we have a good POST-link solution,
    #  or even better, that link is ajax'ed and handles message popups!
    def post(self, request, module_id: int) -> http.HttpResponse:
        module = get_object_or_404(models.Module, pk=module_id)
        count = services.assign_moodle_ids(module=module, created_by=request.user.username)
        messages.success(request, f'{count} moodle ID(s) generated')
        return redirect(module)


class EditHESASubjects(LoginRequiredMixin, PageTitleMixin, generic.detail.SingleObjectMixin, generic.FormView):
    model = models.Module
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


class Uncancel(LoginRequiredMixin, AutoTimestampMixin, PageTitleMixin, SuccessMessageMixin, generic.UpdateView):
    model = models.Module
    form_class = forms.UncancelForm
    template_name = 'module/uncancel.html'
    subtitle = 'Uncancel'
    success_message = 'Course uncancelled'

    def form_valid(self, form) -> http.HttpResponse:
        form.instance.is_cancelled = False
        return super().form_valid(form)


class Cancel(LoginRequiredMixin, AutoTimestampMixin, SuccessMessageMixin, PageTitleMixin, generic.UpdateView):
    model = models.Module
    form_class = forms.CancelForm
    template_name = 'module/cancel.html'
    subtitle = 'Cancel'
    success_message = 'Course cancelled'

    def form_valid(self, form) -> http.HttpResponse:
        module = self.object
        # todo: turn cancel & uncancel into services or model methods
        module.status_id = models.Statuses.CANCELLED
        module.is_cancelled = True
        module.auto_feedback = False
        module.auto_reminder = False

        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        future_fees = TutorPayment.objects.filter(
            tutor_module__module=self.object, status_id__in=[PaymentStatuses.APPROVED, PaymentStatuses.RAISED]
        ).select_related('status', 'tutor_module__tutor__student')

        return {'future_fees': future_fees, **context}


class AddPaymentPlan(LoginRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.CreateView):
    model = ModulePaymentPlan
    title = 'Module'
    subtitle = 'Add payment plan'
    form_class = forms.ModulePaymentPlanForm
    template_name = 'core/form.html'
    success_message = 'Payment plan added: %(plan_type)s'

    def get_initial(self) -> dict:
        return {'module': get_object_or_404(models.Module, pk=self.kwargs['module_id'])}

    def get_success_url(self) -> str:
        return self.object.module.get_absolute_url() + '#payment-plans'


class RemovePaymentPlan(LoginRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.DeleteView):
    model = ModulePaymentPlan
    title = 'Module'
    subtitle = 'Remove payment plan'
    subtitle_object = False
    template_name = 'core/delete_form.html'

    def get_object(self, queryset=None) -> ModulePaymentPlan:
        return get_object_or_404(ModulePaymentPlan, **self.kwargs)

    def get_success_url(self) -> str:
        messages.success(self.request, f'Payment plan removed: {self.object.plan_type}')
        return self.object.module.get_absolute_url() + '#payment-plans'


class ClassRegister(LoginRequiredMixin, MailMergeView):
    def get(self, request, *args, **kwargs) -> http.HttpResponse:
        self.module: models.Module = get_object_or_404(models.Module, pk=self.kwargs['pk'])
        return super().get(request, *args, **kwargs)

    def get_filename(self, queryset) -> str:
        return f'{self.module.code}_register.docx'

    def get_template_file(self, queryset) -> str:
        template = {
            17: 'online_classes.docx',
            32: 'weekly_classes.docx',
            30: 'award_courses.docx',
        }.get(self.module.portfolio.id, 'weekly_classes.docx')
        return str(pathlib.Path(__file__).parent / 'templates/class_registers' / template)

    def get_queryset(self) -> QuerySet:
        return (
            self.module.enrolments.filter(status__takes_place=True)
            .annotate(
                default_email=FilteredRelation('qa__student__email', condition=Q(qa__student__email__is_default=True)),
            )
            .select_related('default_email', 'qa__programme')
            .order_by('qa__student__surname', 'qa__student__firstname')
        )

    def get_merge_data(self) -> dict:
        enrolments = self.get_queryset()

        tutor_module = self.module.tutor_modules.filter(is_teaching=True).first()
        tutor_name = str(tutor_module.tutor.student) if tutor_module else ''

        enrolment_rows = [
            {
                'index': str(index),
                'student': f'{e.qa.student.surname} {e.qa.student.first_or_nickname}',
                'firstname': e.qa.student.firstname,
                'surname': e.qa.student.surname,
                'email': e.default_email.email if hasattr(e, 'default_email') else '',
                'for_credit': 'Yes' if e.for_credit else 'No',
                'cert_he': 'Yes' if e.qa.programme.is_certhe else 'No',
            }
            for index, e in enumerate(enrolments, 1)
        ]

        if len(enrolments) < 25:
            enrolment_rows += [
                # Add a bunch of empty rows to 25
                {'index': str(index + 1)}
                for index in range(len(enrolments), 25)
            ]

        if self.module.start_time and self.module.end_time:
            meeting_time = f"{self.module.start_time:%H:%M} - {self.module.end_time:%H:%M}"
        else:
            meeting_time = self.module.meeting_time

        return {
            'module_code': self.module.code,
            'module_title': self.module.title,
            'day': self.module.start_date.strftime('%A') if self.module.start_date else '',
            'meeting_time': meeting_time,
            'start_date': self.module.start_date.strftime('%d %b %Y') if self.module.start_date else '',
            'end_date': self.module.end_date.strftime('%d %b %Y') if self.module.end_date else '',
            'address': str(self.module.location),
            'tutor_name': tutor_name,
            'row': enrolment_rows,
        }


class Syllabus(LoginRequiredMixin, PageTitleMixin, generic.DetailView):
    """Displays a formatted course syllabus for printing, as part of the weekly classes workflow"""

    model = models.Module
    template_name = 'module/syllabus.html'
    subtitle = 'Syllabus'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        return {
            **context,
            'next_url': next_url_if_safe(self.request),
            # todo: tutor_module & fee logic could be better and refactored to the models
            'tutor_module': self.object.tutor_modules.filter(is_teaching=True).first(),
            'fee': self.object.fees.filter(type=FeeTypes.PROGRAMME).first(),
        }


class AwardPoints(PermissionRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.FormView):
    """Allows staff to edit the results of all enrolments on a module at the same time
    todo: investigate what the ideal tool would look like with colleagues.  Datagrid?  Ajax buttons?
    """

    permission_required = 'enrolment.edit_mark'
    template_name = 'module/award_points.html'
    form_class = forms.AwardPointsFormSet
    title = 'Module'
    subtitle = 'Award points'
    success_message = 'Results updated'
    success_url = '#'

    def dispatch(self, request, *args, **kwargs):
        # can take kwargs or query params, to allow switching modules via a lookup form
        self.object = get_object_or_404(models.Module, pk=self.kwargs.get('pk') or self.request.GET.get('module'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        return {**context, 'switch_module_form': forms.LookupForm}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {**kwargs, 'instance': self.object}

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


# -- Reading list views --


class AddBook(LoginRequiredMixin, PageTitleMixin, AutoTimestampMixin, SuccessMessageMixin, generic.CreateView):
    model = models.Book
    form_class = forms.BookForm
    template_name = 'core/form.html'
    success_message = 'Book added: %(title)s'

    def dispatch(self, request, *args, **kwargs) -> http.HttpResponse:
        self.module = get_object_or_404(models.Module, pk=self.kwargs['module_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form) -> http.HttpResponse:
        form.instance.module = self.module
        return super().form_valid(form)


class EditBook(LoginRequiredMixin, PageTitleMixin, AutoTimestampMixin, SuccessMessageMixin, generic.UpdateView):
    model = models.Book
    form_class = forms.BookForm
    template_name = 'core/form.html'
    success_message = 'Book updated: %(title)s'


class DeleteBook(LoginRequiredMixin, PageTitleMixin, AutoTimestampMixin, SuccessMessageMixin, generic.DeleteView):
    model = models.Book
    template_name = 'core/delete_form.html'

    def get_success_url(self) -> str:
        messages.success(self.request, f'Book deleted: {self.object.title}')
        return self.object.module.get_absolute_url() + '#reading-list'


class RebuildRecommendedReading(LoginRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs) -> http.HttpResponse:
        module = get_object_or_404(models.Module, pk=self.kwargs['pk'])
        services.build_recommended_reading(module=module)
        module.save()
        messages.success(request, 'Reading list text recreated')
        return redirect(module)
