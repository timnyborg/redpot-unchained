from datetime import date

import django_filters as filters
import django_tables2 as tables

from django import forms

from apps.core.utils.datatables import EditLinkColumn, LinkColumn

from . import models


class SearchFilter(filters.FilterSet):
    title = filters.Filter(field_name='title', lookup_expr='unaccent__icontains', label='Title')
    code = filters.Filter(field_name='module__code', lookup_expr='contains', label='Code')

    def hide_past_filter(self, queryset, field_name, value):
        if value:
            return queryset.filter(start_date__gte=date.today())
        return queryset

    hide_past = filters.BooleanFilter(
        label='Hide proposals for past modules',
        method='hide_past_filter',
        initial=True,
        widget=forms.CheckboxInput,
    )

    class Meta:
        model = models.Proposal
        fields = ['title', 'code', 'status', 'hide_past']


class SearchTable(tables.Table):
    edit = EditLinkColumn(verbose_name='')
    impersonate = LinkColumn(
        linkify=lambda record: record.get_external_url(), icon='eye', verbose_name='', title='Impersonate tutor'
    )

    class Meta:
        model = models.Proposal
        fields = ('module__code', "title", "status", "created_on", "reminded_on", "edit", "impersonate")
        per_page = 30
        order_by = ('status', '-created_on')
