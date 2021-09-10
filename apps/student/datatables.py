import re

import django_filters as filters
import django_tables2 as tables

from django import forms
from django.db import models
from django.db.models.functions import Replace

from apps.core.utils.datatables import ViewLinkColumn
from apps.core.utils.widgets import DatePickerInput

from .models import Student


class SearchFilter(filters.FilterSet):
    """An unusually complicated search filter, which does extra filtering on nicknames, default and non-default
    contact details, unaccented filtering
    """

    def filter_firstname(self, queryset, field_name, value) -> models.QuerySet:
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

    birthdate = filters.DateFilter(label='Birthdate', field_name='birthdate', widget=DatePickerInput())

    def filter_postcode(self, queryset, field_name, value) -> models.QuerySet:
        """Finds postcodes starting the same way, while removing spaces from the search and target"""
        value = re.sub(r'\s+', '', value)
        return queryset.annotate(
            trimmed_postcode=Replace('default_address__postcode', models.Value(' '), models.Value(''))
        ).filter(
            trimmed_postcode__startswith=value,
        )

    postcode = filters.CharFilter(
        label='Postcode',
        method='filter_postcode',
    )

    def filter_email(self, queryset, field_name, value) -> models.QuerySet:
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

    def filter_phone(self, queryset, field_name, value) -> models.QuerySet:
        """Filters on (any) phone number, and adds an extra column for the result table to use"""
        value = re.sub(r'\s+', '', value)
        return (
            queryset.annotate(phone_number=models.F('phones__number'))  # for table display
            .alias(stripped_phone_number=Replace('phones__number', models.Value(' '), models.Value('')))
            .filter(stripped_phone_number__contains=value)
            .distinct()
        )

    phone = filters.CharFilter(
        label='Phone',
        method='filter_phone',
    )

    def filter_tutors_only(self, queryset, field_name, value) -> models.QuerySet:
        if value:
            return queryset.filter(tutor__id__isnull=False)
        return queryset

    tutors_only = filters.BooleanFilter(
        label='Tutors only?',
        method='filter_tutors_only',
        widget=forms.CheckboxInput,
    )

    class Meta:
        model = Student
        fields = ('firstname', 'surname', 'birthdate', 'postcode', 'phone', 'email', 'tutors_only')


class SearchTable(tables.Table):
    student = tables.CheckBoxColumn(accessor='id', attrs={'th__input': {'type': 'hidden'}})
    link = ViewLinkColumn('')
    first_or_nickname = tables.Column('First name', order_by='firstname')

    class Meta:
        model = Student
        template_name = "django_tables2/bootstrap.html"
        fields = (
            'student',
            "first_or_nickname",
            "surname",
            "line1",
            "postcode",
            'email_address',
            'husid',
            'phone_number',
        )
        per_page = 10


class CreateMatchTable(tables.Table):
    # Todo view link
    class Meta:
        model = Student
        fields = ['surname', 'firstname', 'birthdate', 'email_address', 'postcode']
        template_name = "django_tables2/bootstrap.html"
        per_page = 30
        orderable = False
