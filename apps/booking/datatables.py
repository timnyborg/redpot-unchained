import django_filters as filters
import django_tables2 as tables

from apps.core.utils.datatables import EditLinkColumn

from . import models


class SearchFilter(filters.FilterSet):
    class Meta:
        model = models.Limit
        fields = {'description': ['contains']}


class SearchTable(tables.Table):
    edit = EditLinkColumn(verbose_name='')

    class Meta:
        model = models.Limit
        fields = ['description', 'places', 'edit']
        order_by = ['description']
