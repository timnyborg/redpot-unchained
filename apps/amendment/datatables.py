import django_filters as filters
import django_tables2 as tables

from django.db.models import QuerySet
from django.forms import widgets
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.core.utils.datatables import EditLinkColumn, PoundsColumn
from apps.core.utils.widgets import DatePickerInput

from . import models


class ApprovalTable(tables.Table):
    amendment = tables.CheckBoxColumn(
        accessor='id',
        attrs={"th__input": {"id": "toggle-all"}},
        orderable=False,
    )
    amount = PoundsColumn()
    student = tables.Column('Student', accessor='enrolment__qa__student', linkify=True)
    module = tables.Column('Module', accessor='enrolment__module', linkify=True)
    requested_by = tables.Column(accessor='requested_by__get_full_name')
    edit = EditLinkColumn(
        verbose_name='', linkify=lambda record: record.get_edit_url() + f'?next={reverse("amendment:approve")}'
    )

    def render_reason(self, record):
        # Provide the details as a tooltip on the reason
        return mark_safe(
            f"""
            <abbr role="button" data-bs-toggle="tooltip" title="{record.details}">
                {record.reason or record.details}
            </abbr>
            """
        )

    class Meta:
        model = models.Amendment
        fields = (
            'amendment',
            'type',
            'student',
            'module',
            'amount',
            'requested_by',
            'requested_on',
            'reason',
            'edit',
        )
        per_page = 20
        order_by = ('pk',)


class SearchFilter(filters.FilterSet):
    type = filters.ModelChoiceFilter(queryset=models.AmendmentType.objects.all(), empty_label='All')
    status = filters.ModelChoiceFilter(queryset=models.AmendmentStatus.objects.all(), empty_label='All')
    completed_before = filters.DateFilter(
        field_name='executed_on',
        lookup_expr='date__lte',
        label='Completed on or before',
        widget=DatePickerInput(),
    )
    completed_after = filters.DateFilter(
        field_name='executed_on',
        lookup_expr='date__gte',
        label='Completed on or after',
        widget=DatePickerInput(),
    )
    id = filters.NumberFilter(field_name='id', label='Reference #')

    def filter_my_requests(self, queryset, field_name, value) -> QuerySet:
        if value:
            return queryset.filter(requested_by=self.request.user)
        return queryset

    my_requests = filters.BooleanFilter(
        method='filter_my_requests', label='My requests', widget=widgets.CheckboxInput()
    )

    class Meta:
        model = models.Amendment
        fields = (
            'type',
            'status',
            'batch',
            'id',
            'completed_before',
            'completed_after',
            'my_requests',
        )


class SearchTable(tables.Table):
    amount = PoundsColumn()
    edit = EditLinkColumn(
        verbose_name='', linkify=lambda record: record.get_edit_url() + f'?next={reverse("amendment:search")}'
    )
    requested_by = tables.Column(accessor='requested_by__get_full_name')

    class Meta:
        model = models.Amendment
        fields = (
            'type',
            'amount',
            'requested_by',
            'requested_on',
            'batch',
            'narrative',
            'status',
            'edit',
        )
        per_page = 20
        order_by = ('-requested_on',)
