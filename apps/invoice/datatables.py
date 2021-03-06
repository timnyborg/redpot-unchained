import django_filters
import django_tables2 as tables

from django import forms
from django.db.models import Q
from django.utils.safestring import mark_safe

from apps.core.utils.datatables import PoundsColumn, ViewLinkColumn
from apps.core.utils.widgets import DatePickerInput, PoundInput
from apps.enrolment.models import Enrolment
from apps.finance.models import Ledger

from .models import Invoice, ScheduledPayment


class InvoiceSearchFilter(django_filters.FilterSet):
    invoiced_to = django_filters.CharFilter(field_name='invoiced_to', label='Invoiced to', lookup_expr='icontains')
    minimum = django_filters.NumberFilter(
        field_name='amount', label='Minimum amount', lookup_expr='gte', widget=PoundInput()
    )
    maximum = django_filters.NumberFilter(
        field_name='amount', label='Maximum amount', lookup_expr='lte', widget=PoundInput()
    )
    created_by = django_filters.CharFilter(field_name='created_by', label='Created by (username)', lookup_expr='exact')
    created_after = django_filters.DateFilter(
        field_name='created_on', label='Created on or after', lookup_expr='gte', widget=DatePickerInput()
    )

    def filter_address(self, queryset, field_name, value):
        """Filters on any invoice address field"""
        if value:
            return queryset.filter(
                Q(line1__icontains=value)
                | Q(line2__icontains=value)
                | Q(line3__icontains=value)
                | Q(town__icontains=value)
                | Q(countystate__icontains=value)
                | Q(country__icontains=value)
                | Q(postcode__icontains=value)
            )
        return queryset

    address = django_filters.CharFilter(
        label='Address',
        method='filter_address',
        help_text="E.g. 'OX1 2JA', 'Sacramento', or 'Mexico'",
    )

    def overdue_only(self, queryset, field_name, value):
        if value:
            return queryset.overdue()
        return queryset

    overdue = django_filters.BooleanFilter(
        label='Overdue only?',
        method='overdue_only',
        widget=forms.CheckboxInput,
    )

    def outstanding_only(self, queryset, field_name, value):
        if value:
            return queryset.outstanding()
        return queryset

    outstanding = django_filters.BooleanFilter(
        label='Outstanding only?',
        method='outstanding_only',
        widget=forms.CheckboxInput,
    )

    class Meta:
        model = Invoice
        fields = [
            'invoiced_to',
            'address',
            'minimum',
            'maximum',
            'created_by',
            'created_after',
            'overdue',
            'outstanding',
        ]


class InvoiceSearchTable(tables.Table):
    view = ViewLinkColumn(verbose_name='')
    number = tables.Column('Number', order_by=("id",))
    amount = PoundsColumn()
    balance = PoundsColumn()

    def render_number(self, record):
        return str(record)  # Get the full invoice number (EQ12345)

    class Meta:
        model = Invoice
        fields = ('number', 'invoiced_to', 'date', 'created_by', 'amount', 'balance')
        per_page = 10
        order_by = ('-date', '-created_on')


class InvoiceFeesTable(tables.Table):
    amount = PoundsColumn()

    class Meta:
        model = Ledger
        fields = ('amount', 'narrative', 'type', 'timestamp', 'enrolment')
        order_by = ('date', 'id')

    enrolment = tables.Column(accessor=tables.A('enrolment'), linkify=True)

    def render_enrolment(self, value):
        return value.module.code


class InvoicePaymentsTable(tables.Table):
    print = tables.Column('', linkify=('unimplemented', {}), accessor='id')
    amount = PoundsColumn()

    class Meta:
        model = Ledger
        fields = ('amount', 'narrative', 'type', 'timestamp')
        order_by = ('date', 'id')

    def render_print(self, record):
        return mark_safe("<i class='fas fa-print'></i>")


class InvoiceCreditNoteTable(tables.Table):
    amount = PoundsColumn()
    invoice = tables.Column(verbose_name='Credit note', accessor='invoice_ledger__invoice', linkify=True)

    class Meta:
        model = Ledger
        fields = ('amount', 'narrative', 'type', 'timestamp', 'invoice')
        order_by = ('date', 'id')


class PaymentScheduleTable(tables.Table):
    amount = PoundsColumn()

    class Meta:
        model = ScheduledPayment
        fields = ('due_date', 'amount', 'is_deposit')
        order_by = ('due_date',)
        orderable = False


class ChooseEnrolmentsTable(tables.Table):
    enrolment = tables.CheckBoxColumn(
        accessor='id',
        attrs={"th__input": {"id": "toggle-all"}},
        orderable=False,
        checked=True,
    )
    balance = PoundsColumn(orderable=False)

    class Meta:
        model = Enrolment
        fields = ('enrolment', 'module__code', 'module__title', 'created_by', 'created_on', 'balance')
        order_by = ('-created_on',)
        per_page = 100


class ChooseFeesTable(tables.Table):
    fee = tables.CheckBoxColumn(
        accessor='id',
        attrs={"th__input": {"id": "toggle-all"}},
        orderable=False,
        checked=True,
    )
    amount = PoundsColumn()
    enrolment = tables.Column(linkify=True)

    def render_enrolment(self, value) -> str:
        return str(value.module.code)

    class Meta:
        model = Ledger
        fields = ('fee', 'amount', 'narrative', 'type', 'date', 'enrolment')
        per_page = 100
