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

from .models import Module
from .forms import ModuleForm
from .datatables import ModuleSearchFilter, ModuleSearchTable, WaitlistTable


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

        enrolments = self.object.enrolments.\
            select_related('result', 'status', 'qa__student').\
            order_by('qa__student__surname', 'qa__student__firstname').\
            all()

        fees = self.object.fees.order_by('-type__display_order', 'description').select_related('type').all()
        programmes = self.object.programmes.order_by('title').select_related('qualification').all()

        tutors = self.object.tutor_modules.\
            select_related('tutor__student').\
            order_by(Coalesce('display_order', 999), 'id').\
            all()

        expense_form_options = expense_forms.template_options(self.object)

        waitlist_table = WaitlistTable(self.object.waitlist.all())

        payment_plans = self.object.payment_plans.all()

        other_runs = None
        if self.object.url:
            other_runs = Module.objects.filter(
                url=self.object.url,
                division=self.object.division
            ).exclude(
                id=self.object.id
            ).order_by(
                F('start_date').desc(nulls_last=True)
            ).all()

        return {
            'enrolments': enrolments,
            'fees': fees,
            'programmes': programmes,
            'tutors': tutors,
            'expense_form_options': expense_form_options,
            'waitlist_table': waitlist_table,
            'payment_plans': payment_plans,
            'other_runs': other_runs,
            **context
        }



    # # Add counter for catering items
    # for fee in fees:
    #     if (fee.fee_type.narrative == 'Catering'):
    #         fee.fee.description = fee.fee.description + ' (' + \
    #                               str(idb((idb.catering.fee == fee.fee.id)
    #                                       & (idb.catering.enrolment == idb.enrolment.id)
    #                                       & (idb.enrolment.status.belongs(10, 90))).count()) + '/' + \
    #                               (str(fee.fee.allocation) if fee.fee.allocation else '∞') + ')'
    #
    # discounts = get_discounts()


    # # Take the first run which is published
    # next_run = other_runs.find(lambda row: row.is_published == True).first()
    # next_run = next_run.id if next_run and next_run.is_published and module.start_date and next_run.start_date and next_run.start_date >= module.start_date else None
    #
    # applications = idb(idb.course_application.module == module.id).select()
    # module_books = idb.book(module=module.id)
    #
    # return dict(publish_form=publish_form, module=module, students=students, fees=fees, programmes=programmes,
    #             tutors=tutors, publish_check=module_publish_check(module.id),
    #             prospectus_check=module_prospectus_check(module.id), other_runs=other_runs,
    #             payment_plans=payment_plans, discounts=discounts, applications=applications,
    #             module_books=module_books, waitlist=waitlist, next_run=next_run)
