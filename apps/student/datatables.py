import django_filters as filters
import django_tables2 as tables

from django.db import models
from django.db.models.functions import Replace

from apps.core.utils.datatables import ViewLinkColumn

from .models import Student


class SearchFilter(filters.FilterSet):
    """An unusually complicated search filter, which does extra filtering on nicknames, default and non-default
    contact details, unaccented filtering
    """

    def filter_firstname(self, queryset, field_name, value):
        """Filters on firstname or nickname, accent-insensitive"""
        return queryset.filter(
            models.Q(firstname__unaccent__startswith=value) | models.Q(nickname__unaccent__startswith=value)
        )

    firstname = filters.CharFilter(label='First name', method='filter_firstname')

    surname = filters.CharFilter(
        label='Surname',
        field_name='surname',
        lookup_expr='unaccent__startswith',
    )

    birthdate = filters.DateFilter(label='Birthdate', field_name='birthdate')

    def filter_postcode(self, queryset, field_name, value):
        """Finds postcodes starting the same way, while removing spaces from the search and target"""
        return queryset.annotate(
            trimmed_postcode=Replace('default_address__postcode', models.Value(' '), models.Value(''))
        ).filter(
            trimmed_postcode__startswith=value.replace(' ', ''),
        )

    postcode = filters.CharFilter(
        label='Postcode',
        method='filter_postcode',
    )

    def filter_email(self, queryset, field_name, value):
        """Filters on (any) email address, and adds an extra column for the result table to use"""
        return (
            queryset.filter(email__email__contains=value)
            .annotate(
                email_address=models.F('email__email'),
            )
            .distinct()
        )

    email = filters.CharFilter(
        label='Email',
        method='filter_email',
    )

    # todo: phone filter

    class Meta:
        model = Student
        fields = ('firstname', 'surname', 'birthdate', 'postcode', 'email')


class SearchTable(tables.Table):
    link = ViewLinkColumn('')
    first_or_nickname = tables.Column('First name', order_by='firstname')

    class Meta:
        model = Student
        template_name = "django_tables2/bootstrap.html"
        fields = ("first_or_nickname", "surname", "line1", "postcode", 'email_address', 'husid')
        per_page = 10


class CreateMatchTable(tables.Table):
    # Todo view link
    class Meta:
        model = Student
        fields = ['surname', 'firstname', 'birthdate', 'email_address', 'postcode']
        template_name = "django_tables2/bootstrap.html"
        per_page = 30
        orderable = False
