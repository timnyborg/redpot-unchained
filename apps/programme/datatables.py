import django_tables2 as tables
from .models import Programme
import django_filters
import django.forms as forms

from apps.main.datatables import ViewLinkColumn


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


class ProgrammeSearchTable(tables.Table):
    link = ViewLinkColumn('')
    qualification = tables.Column(order_by=['qualification__name'])  # override default ordering (elq_rank)

    class Meta:
        model = Programme
        template_name = "django_tables2/bootstrap.html"
        fields = ("title", "division", "portfolio", "qualification",)
        per_page = 10
