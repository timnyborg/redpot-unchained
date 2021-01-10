from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse

from django.template import Template, Context
from django.contrib import messages

from django.db.models import Q

from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView

import django_tables2 as tables
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView

from .models import Programme, QA, ModuleStatus
from .forms import ProgrammeForm
from .datatables import ProgrammeSearchTable, ProgrammeSearchFilter

# Create your views here.

from django.db.models import Count

def view(request, programme_id):
    programme = Programme.objects.get(id=programme_id)

    # counting booleans broken, awaiting new version of mssql backend (https://github.com/ESSolutions/django-mssql-backend/pull/64)
    # enrolment_count = Count('enrolments', filter=Q(enrolments__status__takes_place=1))
    enrolment_count = Count('enrolments', filter=Q(enrolments__status__in=[10, 11, 20, 90]))
    
    modules = programme.modules.annotate(enrolment_count=enrolment_count).select_related('status').order_by('-start_date')[:200].all()
    
    module_count = programme.modules.count()
    students = QA.objects.filter(programme=programme.id).select_related('student').order_by('-start_date')[:200]

    module_statuses = ModuleStatus.objects.all()

    return render(request, 'view.html', context={
        'programme': programme, 
        'modules': modules, 
        'students': students, 
        'module_count': module_count,
        'modules_statuses': module_statuses
    })

class View(DetailView):
    model = Programme
    template_name = 'view.html'

    def get_context_data(self, **kwargs):
        context = super(View, self).get_context_data(**kwargs)
        programme = self.object

        # Get 200 most recent child modules, with a count of enrolment places taken
        enrolment_count = Count('enrolments', filter=Q(enrolments__status__in=[10, 11, 20, 90]))    
        modules = programme.modules.annotate(enrolment_count=enrolment_count).select_related('status').order_by('-start_date')[:200].all()
        
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
   
class Edit(UpdateView):    
    template_name = 'edit.html'
    form_class = ProgrammeForm
    model = Programme    

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        messages.success(self.request, 'Details updated.')
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse('programme:view', args=[self.object.id])
        
        
# def search(request):
    # table = ProgrammeTable()
    # return render(request, 'search.html', context={
        # 'table': table
    # })
    
class Search(SingleTableMixin, FilterView):
    template_name = 'search.html'
    model = Programme
    table_class = ProgrammeSearchTable
    filterset_class = ProgrammeSearchFilter
    