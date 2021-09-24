import django_filters as filters
import django_tables2 as tables

from django import forms
from django.db.models import QuerySet
from django.urls import reverse

from apps.core.utils.datatables import LinkColumn, PoundsColumn
from apps.enrolment.models import Enrolment
from apps.fee.models import Fee

from . import models


class AddFeesTable(tables.Table):
    fee = tables.CheckBoxColumn(
        accessor='id',
        attrs={"th__input": {"id": "toggle-all"}},
        orderable=False,
    )
    amount = PoundsColumn()
    limit = tables.Column(verbose_name='Shared places left', linkify=True, orderable=False)
    places_left = tables.Column(verbose_name='Places left', empty_values=[], orderable=False)

    def render_limit(self, value):
        return value.places_left()

    def render_places_left(self, record):
        if record.is_single_accom:
            return record.module.get_singles_left()
        elif record.is_twin_accom:
            return record.module.get_twins_left()
        elif record.is_catering:
            if record.allocation and record.allocation > 0:
                return record.allocation - record.catering_booking_count()
            return '∞'  # allocation=0 is unlimited
        return '—'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Places and shared places columns appear only if there's data for any row
        self.columns['limit'].column.visible = any(fee.limit for fee in self.data)
        self.columns['places_left'].column.visible = any(
            fee.is_single_accom or fee.is_twin_accom or fee.is_catering for fee in self.data
        )

    class Meta:
        model = Fee
        fields = ('fee', 'description', 'type', 'amount', 'limit', 'places_left')
        order_by = ('type', 'description')


class OutstandingEnrolmentsTable(tables.Table):
    """Lists a series of enrolments with their outstanding balance (for paying multiple at once)"""

    enrolment = tables.CheckBoxColumn(
        accessor='id',
        attrs={"th__input": {"id": "toggle-all"}},
        orderable=False,
    )
    balance = PoundsColumn()

    class Meta:
        model = Enrolment
        fields = (
            'enrolment',
            'qa__student__surname',
            'qa__student__firstname',
            'module__code',
            'module__title',
            'balance',
        )
        order_by = ('-created_on',)
        per_page = 20


class BatchFilter(filters.FilterSet):
    created_by = filters.CharFilter(label='Created by (username)', field_name='created_by', lookup_expr='contains')

    def filter_unbatched(self, queryset, field_name, value) -> QuerySet:
        """Returns null-valued rows if left empty"""
        if value:
            return queryset.unbatched()
        return queryset.batched()

    unbatched = filters.BooleanFilter(label='Unbatched items', method='filter_unbatched', widget=forms.CheckboxInput())

    class Meta:
        model = models.Ledger
        fields = ['created_by', 'batch', 'unbatched']


def batch_link(record: dict):
    # Link to create or view depending on the status
    if record['batch']:
        return reverse('finance:print-batch', args=[record['batch']])
    return reverse('finance:create-batch', args=[record['type'], record['created_by']])


class BatchTable(tables.Table):
    print_column = LinkColumn(verbose_name='', icon='fas fa-print', title='Print', linkify=batch_link)
    type = tables.Column(verbose_name='Transaction type', accessor='type__description')

    class Meta:
        model = models.Ledger
        fields = ['created_by', 'type', 'batch', 'print_column']
        order_by = ['created_by', '-batch']
