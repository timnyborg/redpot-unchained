import django_tables2 as tables
from .models import Invoice
import django_filters
from apps.main.datatables import ViewLinkColumn, PoundsColumn
import django.forms as forms
import django.db.models as models
from datetime import date


class InvoiceSearchFilter(django_filters.FilterSet):
    invoiced_to = django_filters.CharFilter(field_name='invoiced_to', label='Invoiced to', lookup_expr='icontains')
    minimum = django_filters.NumberFilter(field_name='amount', label='Minimum amount', lookup_expr='gte')
    maximum = django_filters.NumberFilter(field_name='amount', label='Maximum amount', lookup_expr='lte')
    created_by = django_filters.CharFilter(field_name='created_by', label='Created by (username)', lookup_expr='exact')
    created_after = django_filters.DateFilter(field_name='created_on', label='Created on or after', lookup_expr='gte')

    def overdue_only(self, queryset, field_name, value):
        if value:
            # Subquery - get a list of invoices with ledger totals > 0
            outstanding = Invoice.objects.annotate(
                balance=models.Sum('allocated_ledger_items__amount')
            ).filter(balance__gt=0).values('id')
            # Apply a filter to the queryset, limiting it to those outstanding invoices, plus check they're overdue
            return queryset.filter(due_date__lt=date.today()).filter(id__in=outstanding)
        return queryset

    Overdue = django_filters.BooleanFilter(
        label='Overdue only?',
        method='overdue_only',
        widget=forms.CheckboxInput
    )

    def outstanding_only(self, queryset, field_name, value):
        if value:
            # Subquery - get a list of invoices with ledger totals > 0
            outstanding = Invoice.objects.annotate(
                balance=models.Sum('allocated_ledger_items__amount')
            ).filter(balance__gt=0).values('id')
            # Apply a filter to the queryset, limiting it to those outstanding invoices
            return queryset.filter(id__in=outstanding)
        return queryset

    Outstanding = django_filters.BooleanFilter(
        label='Outstanding only?',
        method='outstanding_only',
        widget=forms.CheckboxInput
    )

    def address(self, queryset, field_name, value):
        if value:
            return queryset # TODO: Implement
        return queryset

    class Meta:
        model = Invoice
        fields = []  # all defined above


class InvoiceSearchTable(tables.Table):
    view = ViewLinkColumn(verbose_name='')
    full_number = tables.Column('Number', order_by=("id",))
    amount = PoundsColumn()
    balance = PoundsColumn()

    class Meta:
        model = Invoice
        template_name = "django_tables2/bootstrap.html"
        fields = ('full_number', 'invoiced_to', 'date', 'created_by', 'amount', 'balance')
        per_page = 10
        order_by = ('-date', '-created_on',)
