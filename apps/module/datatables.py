from datetime import date

import django_filters
import django_tables2 as tables
from dateutil.relativedelta import relativedelta

import django.forms as forms

from apps.core.utils.datatables import DeleteLinkColumn, EditLinkColumn, LinkColumn, ViewLinkColumn
from apps.waitlist.models import Waitlist

from . import models


class ModuleSearchFilter(django_filters.FilterSet):
    def limit_years_filter(self, queryset, field_name, value):
        if value:
            date_threshold = date.today() - relativedelta(years=3)
            return queryset.filter(start_date__gte=date_threshold)
        return queryset

    limit_years = django_filters.BooleanFilter(
        label='Limit to last three years',
        method='limit_years_filter',
        initial=True,
        widget=forms.CheckboxInput,
    )

    # Override the label while maintaining order.  Awkward.  Might as well do a custom order in the template
    title__unaccent__icontains = django_filters.Filter(
        field_name='title',
        lookup_expr='unaccent__icontains',
        label='Title',
    )

    class Meta:
        model = models.Module
        fields = {
            'title': ['unaccent__icontains'],
            'code': ['contains'],
            'division': ['exact'],
            'portfolio': ['exact'],
        }


class ModuleSearchTable(tables.Table):
    view = ViewLinkColumn(verbose_name='')
    start_date = tables.Column(attrs={"td": {"style": "white-space: nowrap;"}})
    end_date = tables.Column(attrs={"td": {"style": "white-space: nowrap;"}})

    class Meta:
        model = models.Module
        fields = ('code', "title", "start_date", "end_date", "division", "portfolio")
        per_page = 10
        order_by = ('-start_date',)


class WaitlistTable(tables.Table):
    id = tables.CheckBoxColumn(accessor='id', orderable=False)
    student = tables.Column(linkify=True)
    email = LinkColumn('', icon='envelope', title='Email student', linkify=lambda record: f'email-one/{record.id}')
    delete = DeleteLinkColumn('', title='Remove from waiting list')

    class Meta:
        model = Waitlist
        fields = ('id', 'student', 'listed_on', 'emailed_on')


class BookTable(tables.Table):
    edit = EditLinkColumn('')
    delete = DeleteLinkColumn('')

    class Meta:
        model = models.Book
        fields = ('author', 'title', 'type')
        order_by = ('-type', 'author', 'title')
