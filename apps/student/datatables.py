from django.db import models

import django_tables2 as tables
import django_filters

from apps.core.utils.datatables import ViewLinkColumn

from .models import Student


class StudentSearchFilter(django_filters.FilterSet):
    """An unusually complicated search filter, which does extra filtering on nicknames, default and non-default
       contact details, unaccented filtering
    """
    def filter_firstname(self, queryset, field_name, value):
        """Filters on firstname or nickname, accent-insensitive"""
        return queryset.filter(
            models.Q(firstname__unaccent__startswith=value)
            | models.Q(nickname__unaccent__startswith=value)
        )

    firstname = django_filters.CharFilter(
        label='First name',
        method='filter_firstname'
    )

    surname = django_filters.CharFilter(
        label='Surname',
        field_name='surname',
        lookup_expr='unaccent__startswith',
    )

    birthdate = django_filters.DateFilter(
        label='Birthdate',
        field_name='birthdate'
    )

    def filter_postcode(self, queryset, field_name, value):
        """Filters on the (default) address postcode"""
        return queryset.filter(
            address__is_default=True,
            address__postcode__startswith=value,
        )

    postcode = django_filters.CharFilter(
        label='Postcode',
        method='filter_postcode',
    )

    def filter_email(self, queryset, field_name, value):
        """Filters on (any) email address, and adds an extra column for the result table to use"""
        return queryset.filter(
            email__email__contains=value
        ).annotate(
            email_address=models.F('email__email'),
        )

    email = django_filters.CharFilter(
        label='Email',
        method='filter_email',
    )

    # todo: phone filter

    class Meta:
        model = Student
        fields = {}  # All defined above


class StudentSearchTable(tables.Table):
    link = ViewLinkColumn('')
    first_or_nickname = tables.Column('First name')

    class Meta:
        model = Student
        template_name = "django_tables2/bootstrap.html"
        fields = ("first_or_nickname", "surname", "line1", "postcode", 'email_address', 'husid')
        per_page = 10
