import textwrap

import django_filters as filters
import django_tables2 as tables

from django import forms
from django.db.models import QuerySet

from apps.contract import models
from apps.core.utils.datatables import ViewLinkColumn


class OutstandingTable(tables.Table):
    """Lists contracts needing approval or signature (depending on the queryset) with a checkbox column"""

    contract = tables.CheckBoxColumn(accessor='id', attrs={"th__input": {"id": "toggle-all"}}, orderable=False)
    view = ViewLinkColumn(verbose_name='', attrs={'a': {'target': '_blank'}})

    class Meta:
        model = models.Contract
        fields = [
            'contract',
            'tutor_module__tutor__student__surname',
            'tutor_module__tutor__student__firstname',
            'tutor_module__module__code',
            'tutor_module__module__title',
            'tutor_module__module__start_date',
            'tutor_module__module__end_date',
            'view',
        ]


class SearchFilter(filters.FilterSet):
    module_code = filters.CharFilter(
        field_name='tutor_module__module__code', lookup_expr='contains', label='Module code'
    )
    firstname = filters.CharFilter(
        field_name='tutor_module__tutor__student__firstname', lookup_expr='exact', label='First name'
    )
    surname = filters.CharFilter(
        field_name='tutor_module__tutor__student__surname', lookup_expr='exact', label='Surname'
    )
    created_by = filters.CharFilter(label='Created by (username)')

    def filter_my_contracts(self, queryset, field_name, value) -> QuerySet:
        if value:
            return queryset.filter(created_by=self.request.user.username)
        return queryset

    my_contracts = filters.BooleanFilter(
        label='My contracts', method='filter_my_contracts', widget=forms.CheckboxInput()
    )

    class Meta:
        model = models.Contract
        fields = ['module_code', 'status', 'firstname', 'surname', 'created_by', 'my_contracts']


class SearchTable(tables.Table):
    link = ViewLinkColumn(verbose_name='')
    start_date = tables.Column(accessor='tutor_module__module__start_date', attrs={'td': {'class': 'text-nowrap'}})
    title = tables.Column(accessor='tutor_module__module__title')

    def render_title(self, value) -> str:
        return textwrap.shorten(value, 50, placeholder=' ...')

    class Meta:
        model = models.Contract
        fields = [
            'tutor_module__tutor__student__surname',
            'tutor_module__tutor__student__firstname',
            'tutor_module__module__code',
            'title',
            'status',
            'start_date',
            'created_by',
        ]
