import django_tables2 as tables
from .models import Module, ModuleWaitlist
import django_filters
from apps.main.utils.datatables import DeleteLinkColumn, LinkColumn, ViewLinkColumn
import django.forms as forms
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

    # Override the label while maintaining order.  Awkward.  Might as well do a custom order in the template
    title__unaccent__icontains = django_filters.Filter(field_name='title', lookup_expr='unaccent__icontains', label='Title')
    
    class Meta:
        model = Module
        fields = {
            'title': ['unaccent__icontains'],
            'code': ['startswith'],
            'division': ['exact'],
            'portfolio': ['exact'],
        }        


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


class WaitlistTable(tables.Table):
    id = tables.CheckBoxColumn(
        accessor='id',
        orderable=False
    )

    email = LinkColumn('', icon='envelope', title='Email student', linkify=lambda record: f'email-one/{record.id}')
    delete = DeleteLinkColumn('', title='Remove from waiting list')

    class Meta:
        model = ModuleWaitlist
        template_name = "django_tables2/bootstrap.html"
        fields = ('id', 'student', 'listed_on', 'emailed_on')


