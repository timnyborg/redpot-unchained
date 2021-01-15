from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Q, Count

from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.detail import DetailView

from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView

from django.contrib.messages.views import SuccessMessageMixin

from apps.main.forms import PageTitleMixin
from apps.module.models import ModuleStatus
from .models import Programme, QA
from .forms import ProgrammeEditForm, ProgrammeNewForm
from .datatables import ProgrammeSearchTable, ProgrammeSearchFilter


class View(LoginRequiredMixin, PageTitleMixin, DetailView):
    model = Programme
    template_name = 'programme/view.html'

    def get_context_data(self, **kwargs):
        context = super(View, self).get_context_data(**kwargs)
        programme = self.object

        # Get 200 most recent child modules, with a count of enrolment places taken
        enrolment_count = Count('enrolments', filter=Q(enrolments__status__in=[10, 11, 20, 90]))    
        modules = programme.modules.annotate(enrolment_count=enrolment_count
                                             ).select_related('status').order_by('-start_date')[:200].all()
        
        module_count = programme.modules.count()
        students = QA.objects.filter(programme=programme.id).select_related('student').order_by('-start_date')[:200]

        module_statuses = ModuleStatus.objects.all()

        return {
            **context,
            'modules': modules, 
            'students': students, 
            'module_count': module_count,
            'modules_statuses': module_statuses
        }


class Edit(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, UpdateView):
    model = Programme    
    form_class = ProgrammeEditForm
    template_name = 'programme/edit.html'
    success_message = 'Details updated.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user
        })
        return kwargs

    def form_valid(self, form):
        form.instance.modified_on = datetime.now()
        form.instance.modified_by = self.request.user.username
        return super().form_valid(form)


class New(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, CreateView):
    model = Programme
    form_class = ProgrammeNewForm
    template_name = 'programme/edit.html'
    success_message = 'Details updated.'

    def form_valid(self, form):
        # No need to handle created_on or modified_on as they use auto_now_add=True
        form.instance.modified_by = self.request.user.username
        form.instance.created_by = self.request.user.username
        return super().form_valid(form)
    
class Search(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    template_name = 'programme/search.html'
    model = Programme
    table_class = ProgrammeSearchTable
    filterset_class = ProgrammeSearchFilter
    subtitle = 'Search'

    