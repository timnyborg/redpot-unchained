import django_tables2 as tables
from django.urls import reverse
from .models import Module
from django.utils.html import format_html
import django_filters

import django.forms as forms
import django.db.models as models
from datetime import date
from dateutil.relativedelta import relativedelta


class ModuleSearchFilter(django_filters.FilterSet):
    def limit_years(self, queryset, field_name, value):
        if value:
            date_threshold = date.today() - relativedelta(years=3)
            return queryset.filter(start_date__gte=date_threshold)
        return queryset

    has_category = django_filters.BooleanFilter(
        label='Limit to last three years',
        method='limit_years',
        initial=True,
        widget=forms.CheckboxInput
    )
    
    class Meta:
        model = Module
        fields = {
            'title': ['unaccent__icontains'],
            'code': ['startswith'],
            'division': ['exact'],
            'portfolio': ['exact'],
            # 'is_active': ['exact'],
        }        
        
        filter_overrides = {
            models.BooleanField: {
                'filter_class': django_filters.BooleanFilter,
                'extra': lambda f: {
                   'widget': forms.CheckboxInput,
                },
            },
        }


class ViewLinkColumn(tables.Column):
    empty_values=() # Prevents the table from rendering Nothing, since it's an entirely generated column

    def render(self, record):
        # url = reverse('module:view', args=[record.id])
        url = ''
        return format_html(f'<a href="{url}"><span class="fa fa-search" alt="View"></span></a>')    
        
    def __init__(self, *args, **kwargs):
        # Always disable sorting and header.  Avoids having to say so every time it's used: view = ViewLinkColumn(orderable=False)
        kwargs.update({
            'orderable': False,
            'verbose_name': '',
        })
        super(ViewLinkColumn, self).__init__(*args, **kwargs)


class ModuleSearchTable(tables.Table):
    view = ViewLinkColumn(verbose_name='')
    start_date = tables.Column(attrs={"td": {"style": "white-space: nowrap;"}})
    end_date = tables.Column(attrs={"td": {"style": "white-space: nowrap;"}})
    # qualification = tables.Column(order_by=['qualification__name'])  # override default ordering (elq_rank)
    
    class Meta:
        model = Module
        template_name = "django_tables2/bootstrap.html"
        fields = ('code', "title", "start_date", "end_date", "division", "portfolio",)
        per_page = 10
        order_by = ('-start_date',)