from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DetailView, UpdateView

from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin
from apps.discount.models import Discount
from apps.tutor.utils import expense_forms

from .datatables import BookTable, ModuleSearchFilter, ModuleSearchTable, WaitlistTable
from .forms import CreateForm, EditForm
from .models import Module, ModuleStatus


class Edit(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, AutoTimestampMixin, UpdateView):
    model = Module
    form_class = EditForm
    template_name = 'module/edit.html'
    success_message = 'Details updated.'


class New(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, AutoTimestampMixin, CreateView):
    form_class = CreateForm
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
    model = Module
    table_class = ModuleSearchTable
    filterset_class = ModuleSearchFilter
    subtitle = 'Search'


class View(LoginRequiredMixin, PageTitleMixin, DetailView):
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
