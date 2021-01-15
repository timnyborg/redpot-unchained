from django.shortcuts import render

from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView

from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from apps.main.forms import PageTitleMixin

from .models import Module
from .forms import ModuleForm
from .datatables import ModuleSearchFilter, ModuleSearchTable

# Create your views here.

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
