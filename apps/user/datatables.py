import django_filters as filters
import django_tables2 as tables

from django import forms

from apps.core.models import User
from apps.core.utils.datatables import EditLinkColumn, ViewLinkColumn


class SearchFilter(filters.FilterSet):
    first_name = filters.CharFilter(label='First name', lookup_expr='contains')
    last_name = filters.CharFilter(label='Last name', lookup_expr='contains')
    username = filters.CharFilter(label='Username', lookup_expr='contains')
    role = filters.CharFilter(label='Role', lookup_expr='contains')

    def show_inactive_filter(self, queryset, field_name, value):
        if value:
            return queryset.filter(is_active=True)
        return queryset

    show_inactive = filters.BooleanFilter(
        label='Include inactive users',
        method='show_inactive_filter',
        widget=forms.CheckboxInput,
    )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'role',
            'show_inactive',
        )


class SearchTable(tables.Table):
    edit = EditLinkColumn()
    view = ViewLinkColumn()

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'role',
            'edit',
            'view',
        )
        per_page = 20
        order_by = ('first_name', 'last_name')
