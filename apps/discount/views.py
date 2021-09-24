import django_tables2 as tables
from django_filters.views import FilterView

from django.contrib.auth.mixins import LoginRequiredMixin

from apps.core.utils.views import PageTitleMixin

from . import datatables, models


class Search(LoginRequiredMixin, PageTitleMixin, tables.SingleTableMixin, FilterView):
    queryset = models.Discount.objects.select_related('portfolio')
    table_class = datatables.SearchTable
    filterset_class = datatables.SearchFilter
    subtitle = 'Search'
    template_name = 'core/search.html'
