import django_filters
import django_tables2

from django.db.models import Q

from apps.core.utils.datatables import EditLinkColumn, PoundsColumn
from apps.programme.models import Division, Portfolio

from .models import TutorFee


class SearchFilter(django_filters.FilterSet):
    def filter_module(self, queryset, field_name, value):
        """Filters on code or title"""
        if value:
            return queryset.filter(
                Q(tutor_module__module__code__startswith=value)
                | Q(tutor_module__module__title__unaccent__icontains=value)
            )
        return queryset

    module = django_filters.Filter(
        label='Module',
        help_text='Title or code',
        method='filter_module',
    )
    division = django_filters.ModelChoiceFilter(
        field_name='tutor_module__module__division', label='Division', queryset=Division.objects.all()
    )
    portfolio = django_filters.ModelChoiceFilter(
        field_name='tutor_module__module__portfolio', label='Portfolio', queryset=Portfolio.objects.all()
    )
    firstname = django_filters.Filter(
        field_name='tutor_module__tutor__student__firstname',
        lookup_expr='startswith',
        label='First name',
    )
    surname = django_filters.Filter(
        field_name='tutor_module__tutor__student__surname',
        lookup_expr='startswith',
        label='Surname',
    )

    class Meta:
        model = TutorFee
        fields = [
            'status',
            'module',
            'division',
            'portfolio',
            'firstname',
            'surname',
            'raised_by',
            'batch',
        ]


class SearchTable(django_tables2.Table):
    approvable_icon = django_tables2.TemplateColumn(
        verbose_name='', template_name='tutor_payment/approvable_icon_column.html'
    )
    amount = PoundsColumn()
    edit = EditLinkColumn('')

    class Meta:
        model = TutorFee
        template_name = "django_tables2/bootstrap.html"
        fields = (
            'approvable_icon',
            'tutor_module__tutor__student',
            'tutor_module__module__code',
            'amount',
            'type',
            'raised_by',
            'approved_by',
            'transferred_on',
            'status',
            'batch',
            'edit',
        )
        per_page = 15
        order_by = ('-raised_on',)
