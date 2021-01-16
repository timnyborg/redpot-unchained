import django_tables2 as tables
from .models import Programme
from django.utils.html import format_html
import django_filters

import django.forms as forms


class ProgrammeSearchFilter(django_filters.FilterSet):    
    show_inactive_filter = django_filters.BooleanFilter(
        label='Show inactive programmes',
        method='show_inactive',
        widget=forms.CheckboxInput,
        initial=False
    )
    
    class Meta:
        model = Programme
        # everything else is standard, so the meta approach is simplest
        fields = {
            'title': ['icontains'],
            'division': ['exact'],
            'portfolio': ['exact'],
            'qualification': ['exact'],
        }

    def show_inactive(self, queryset, name, value):
        if value:
            return queryset
        return queryset.filter(is_active=True)


class ViewLinkColumn(tables.Column):
    empty_values = ()  # Prevents the table from rendering Nothing, since it's an entirely generated column

    def render(self, record): 
        return format_html('<span class="fas fa-search" alt="View"></span>')    
        
    def __init__(self, verbose_name, **kwargs):
        # Always disable sorting and header.
        # Avoids having to say so every time it's used: view = ViewLinkColumn(orderable=False...)
        kwargs.update({
            'orderable': False,
            'linkify': True,  # wraps render() in an <a> linking to get_absolute_url()
            'accessor': 'id',  # could be literally anything on the
            'exclude_from_export': True,
        })
        super(ViewLinkColumn, self).__init__(verbose_name=verbose_name, **kwargs)     


class ProgrammeSearchTable(tables.Table):
    link = ViewLinkColumn('')
    qualification = tables.Column(order_by=['qualification__name'])  # override default ordering (elq_rank)

    class Meta:
        model = Programme
        template_name = "django_tables2/bootstrap.html"
        fields = ("title", "division", "portfolio", "qualification",)
        per_page = 10
