from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView

from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.functions import Coalesce

from apps.main.utils.views import PageTitleMixin
from apps.tutor.utils import expense_forms
from apps.discount.models import Discount

from .models import Module, ModuleStatus
from .forms import ModuleForm
from .datatables import ModuleSearchFilter, ModuleSearchTable, WaitlistTable, BookTable


class Edit(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, UpdateView):
    model = Module
    form_class = ModuleForm
    template_name = 'module/edit.html'
    success_message = 'Details updated.'


class Search(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    template_name = 'module/search.html'
    model = Module
    table_class = ModuleSearchTable
    filterset_class = ModuleSearchFilter
    subtitle = 'Search'


class View(LoginRequiredMixin, PageTitleMixin, DetailView):
    queryset = Module.objects.defer()  # Get all fields
    template_name = 'module/view.html'

    def get_context_data(self, **kwargs):
        context = super(View, self).get_context_data(**kwargs)

        enrolments = (
            self.object.enrolments
            .select_related('result', 'status', 'qa__student')
            .order_by('qa__student__surname', 'qa__student__firstname')
        )

        fees = self.object.fees.order_by('-type__display_order', 'description').select_related('type').all()
        programmes = self.object.programmes.order_by('title').select_related('qualification').all()

        tutors = (
            self.object.tutor_modules
            .select_related('tutor__student')
            .order_by(Coalesce('display_order', 999), 'id')
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
            **context
        }
