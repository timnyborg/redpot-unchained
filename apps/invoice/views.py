from django.shortcuts import render

from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView

from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from apps.main.forms import PageTitleMixin

from .models import Invoice
from .datatables import InvoiceSearchFilter, InvoiceSearchTable


class Search(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    template_name = 'invoice/search.html'
    model = Invoice
    table_class = InvoiceSearchTable
    filterset_class = InvoiceSearchFilter
    subtitle = 'Search'
