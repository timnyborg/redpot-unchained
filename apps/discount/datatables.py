from datetime import datetime

import django_filters as filters
import django_tables2 as tables

from django.db.models import Q, QuerySet
from django.forms import CheckboxInput

from apps.core.utils.datatables import EditLinkColumn
from apps.discount import models


class SearchFilter(filters.FilterSet):
    code = filters.CharFilter(lookup_expr='contains', label='Code')
    name = filters.CharFilter(lookup_expr='contains', label='Name')

    def filter_expired(self, queryset, field_name, value) -> QuerySet:
        if not value:
            return queryset.filter(Q(expires_on__gt=datetime.now()) | Q(expires_on__isnull=True))
        return queryset

    include_expired = filters.BooleanFilter(label='Include expired?', method='filter_expired', widget=CheckboxInput)

    class Meta:
        model = models.Discount
        fields = ['code', 'name', 'include_expired']


class SearchTable(tables.Table):
    edit = EditLinkColumn(verbose_name='')

    def render_percent(self, value) -> str:
        return f'{value}%'

    class Meta:
        model = models.Discount
        fields = [
            'name',
            'code',
            'percent',
            'expires_on',
            'module_mask',
            'portfolio',
            'edit',
        ]
        order_by = ['-created_on']
