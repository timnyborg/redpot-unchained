from django.shortcuts import render

from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView

from .models import Module
from .datatables import ModuleSearchFilter, ModuleSearchTable

# Create your views here.
class Search(SingleTableMixin, FilterView):
    template_name = 'module/search.html'
    model = Module
    table_class = ModuleSearchTable
    filterset_class = ModuleSearchFilter
    