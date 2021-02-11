from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView

from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.functions import Coalesce
from django.db.models.expressions import F

from apps.main.utils.views import PageTitleMixin
from apps.tutor.utils import expense_forms
from apps.discount.utils import get_module_discounts

from .models import Module
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
    model = Module
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

        payment_plans = self.object.payment_plans.all()
        book_table = BookTable(self.object.books.all())

        discounts = get_module_discounts(self.object)

        other_runs = next_run = None
        if self.object.url:
            other_runs = (
                Module.objects
                .filter(url=self.object.url, division=self.object.division)
                .exclude(id=self.object.id)
                .order_by(F('start_date').desc(nulls_last=True))
            )

            next_run = other_runs.filter(
                is_published=True,
                start_date__gte=self.object.start_date
            ).order_by('-start_date').first()
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
            **context
        }

    # applications = idb(idb.course_application.module == module.id).select()
