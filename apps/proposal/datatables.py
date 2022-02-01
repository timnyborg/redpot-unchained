from datetime import date

import django_filters as filters
import django_tables2 as tables

from django import forms

from apps.core.utils.datatables import EditLinkColumn, LinkColumn

from . import models


class SearchFilter(filters.FilterSet):
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
        fields = ['status', 'hide_past']


class SearchTable(tables.Table):
    edit = EditLinkColumn(verbose_name='')
    impersonate = LinkColumn(linkify='#', icon='eye', verbose_name='')  # todo: link up

    class Meta:
        model = models.Proposal
        fields = ('module__code', "title", "status", "created_on", "reminded_on", "edit", "impersonate")
        per_page = 30
        order_by = ('status', '-created_on')
