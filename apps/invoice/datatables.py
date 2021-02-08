import django_tables2 as tables
from .models import Invoice, Ledger
import django_filters
from apps.main.utils.datatables import ViewLinkColumn, PoundsColumn
import django.forms as forms
from django.utils.html import mark_safe

class InvoiceSearchFilter(django_filters.FilterSet):
    invoiced_to = django_filters.CharFilter(field_name='invoiced_to', label='Invoiced to', lookup_expr='icontains')
    minimum = django_filters.NumberFilter(field_name='amount', label='Minimum amount', lookup_expr='gte')
    maximum = django_filters.NumberFilter(field_name='amount', label='Maximum amount', lookup_expr='lte')
    created_by = django_filters.CharFilter(field_name='created_by', label='Created by (username)', lookup_expr='exact')
    created_after = django_filters.DateFilter(field_name='created_on', label='Created on or after', lookup_expr='gte')

    def overdue_only(self, queryset, field_name, value):
        if value:
            return queryset.overdue()
        return queryset

    Overdue = django_filters.BooleanFilter(
        label='Overdue only?',
        method='overdue_only',
        widget=forms.CheckboxInput
    )

    def outstanding_only(self, queryset, field_name, value):
        if value:
            return queryset.outstanding()
        return queryset

    Outstanding = django_filters.BooleanFilter(
        label='Outstanding only?',
        method='outstanding_only',
        widget=forms.CheckboxInput
    )

    def address(self, queryset, field_name, value):
        if value:
            return queryset  # TODO: Implement
        return queryset

    class Meta:
        model = Invoice
        fields = []  # all defined above


class InvoiceSearchTable(tables.Table):
    view = ViewLinkColumn(verbose_name='')
    number = tables.Column('Number', order_by=("id",))
    amount = PoundsColumn()
    balance = PoundsColumn()

    def render_number(self, record):
        return str(record)  # Get the full invoice number (EQ12345)

    class Meta:
        model = Invoice
        template_name = "django_tables2/bootstrap.html"
        fields = ('number', 'invoiced_to', 'date', 'created_by', 'amount', 'balance')
        per_page = 10
        order_by = ('-date', '-created_on',)


class InvoiceFeesTable(tables.Table):
    amount = PoundsColumn()

    class Meta:
        model = Ledger
        template_name = "django_tables2/bootstrap.html"
        fields = ('amount', 'narrative', 'type', 'date', 'enrolment')
        order_by = ('date', 'id')

    enrolment = tables.Column(accessor=tables.A('enrolment'), linkify=True)

    def render_enrolment(self, value):
        return value.module.code


class InvoicePaymentsTable(tables.Table):
    print = tables.Column('', linkify=('unimplemented', {}), accessor='id')
    amount = PoundsColumn()

    class Meta:
        model = Ledger
        template_name = "django_tables2/bootstrap.html"
        fields = ('amount', 'narrative', 'type', 'date')
        order_by = ('date', 'id')

    def render_print(self, record):
        return mark_safe("<i class='fas fa-print'></i>")