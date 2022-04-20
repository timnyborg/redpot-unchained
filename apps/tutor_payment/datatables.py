import textwrap

import django_filters as filters
import django_tables2 as tables
from dal import autocomplete

from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.core.models import Division, Portfolio, User
from apps.core.utils.datatables import EditLinkColumn, PoundsColumn

from . import models
from .models import TutorPayment


class SearchFilter(filters.FilterSet):
    def filter_module(self, queryset, field_name, value):
        """Filters on code or title"""
        if value:
            return queryset.filter(
                Q(tutor_module__module__code__startswith=value)
                | Q(tutor_module__module__title__unaccent__icontains=value)
            )
        return queryset

    module = filters.Filter(
        label='Module',
        help_text='Title or code',
        method='filter_module',
    )
    division = filters.ModelChoiceFilter(
        field_name='tutor_module__module__division', label='Division', queryset=Division.objects.all()
    )
    portfolio = filters.ModelChoiceFilter(
        field_name='tutor_module__module__portfolio', label='Portfolio', queryset=Portfolio.objects.all()
    )
    firstname = filters.Filter(
        field_name='tutor_module__tutor__student__firstname',
        lookup_expr='startswith',
        label='First name',
    )
    surname = filters.Filter(
        field_name='tutor_module__tutor__student__surname',
        lookup_expr='startswith',
        label='Surname',
    )
    raised_by = filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2Multiple('autocomplete:user'),
    )

    class Meta:
        model = TutorPayment
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['raised_by'].field.label_from_instance = lambda obj: obj.get_full_name()


class SearchTable(tables.Table):
    raised_by = tables.Column(
        accessor='raised_by__get_full_name',
        order_by=('raised_by__first_name', 'raised_by__last_name'),
    )
    approvable_icon = tables.TemplateColumn(verbose_name='', template_name='tutor_payment/approvable_icon_column.html')
    amount = PoundsColumn()
    edit = EditLinkColumn('')

    class Meta:
        model = TutorPayment
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


class ApprovalFilter(filters.FilterSet):
    raised_by = filters.ModelChoiceFilter(queryset=User.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['raised_by'].field.label_from_instance = lambda obj: obj.get_full_name()
        # Limit the dropdown to users in the queryset
        self.filters['raised_by'].field.queryset = User.objects.filter(username__in=self.queryset.values('raised_by'))


class ApprovalTable(tables.Table):
    payment = tables.CheckBoxColumn(
        accessor='id',
        attrs={"th__input": {"id": "toggle-all"}},
        orderable=False,
    )
    approvable_icon = tables.TemplateColumn(verbose_name='', template_name='tutor_payment/approvable_icon_column.html')
    tutor = tables.Column(
        verbose_name='Tutor',
        accessor='tutor_module__tutor__student',
        linkify=True,
        order_by=('tutor_module__tutor__student__surname', 'tutor_module__tutor__student__firstname'),
    )
    title = tables.Column(
        accessor='tutor_module__module__title', linkify=lambda record: record.tutor_module.module.get_absolute_url()
    )
    start_date = tables.Column(accessor='tutor_module__module__start_date', attrs={'td': {'class': 'text-nowrap'}})
    amount = PoundsColumn()
    type = tables.Column(accessor='type__short_form')
    raised_by = tables.Column(
        accessor='raised_by__get_full_name',
        order_by=('raised_by__first_name', 'raised_by__last_name'),
    )
    raised_on = tables.Column(accessor='raised_on__date', attrs={'td': {'class': 'text-nowrap'}})
    edit = EditLinkColumn(
        verbose_name='', linkify=lambda record: record.get_edit_url() + f'?next={reverse("tutor-payment:approve")}'
    )

    def render_details(self, record):
        if len(record.details) < 70:
            return record.details
        truncated = textwrap.shorten(record.details, 50, placeholder='...')
        return mark_safe(f'<span role="button" data-bs-toggle="tooltip" title="{record.details}">{truncated}</abbr>')

    class Meta:
        model = models.TutorPayment
        fields = (
            'payment',
            'approvable_icon',
            'tutor',
            'title',
            'start_date',
            'amount',
            'type',
            'raised_by',
            'raised_on',
            'details',
            'edit',
        )
        per_page = 20
        order_by = ('pk',)
