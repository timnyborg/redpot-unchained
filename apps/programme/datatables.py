import django_tables2 as tables
from django.urls import reverse
from .models import Programme
from django.utils.html import format_html


import django_filters

from apps.main.forms import Bootstrap3FormMixin

import django.forms as forms
import django.db.models as models

class ProgrammeSearchFilter(django_filters.FilterSet):        
    class Meta:
        model = Programme
        fields = {
            'title': ['icontains'],
            'division': ['exact'],
            'portfolio': ['exact'],
            'qualification': ['exact'],
            'is_active': ['exact'],
        }
        form = Bootstrap3FormMixin  
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
        url = reverse('programme:view', args=[record.id])
        return format_html(f'<a href="{url}"><span class="fa fa-search" alt="View"></span></a>')    
        
    def __init__(self, *args, **kwargs):
        # Always disable sorting and header.  Avoids having to say so every time it's used: view = ViewLinkColumn(orderable=False)
        kwargs.update({
            'orderable': False,
            'verbose_name': '',
        })
        super(ViewLinkColumn, self).__init__(*args, **kwargs)

class ProgrammeSearchTable(tables.Table):
    view = ViewLinkColumn(verbose_name='')
    class Meta:
        model = Programme
        template_name = "django_tables2/bootstrap.html"
        fields = ("title", "division", "portfolio", "qualification",)
        per_page = 10