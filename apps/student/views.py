from django.contrib.auth.mixins import LoginRequiredMixin

from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView
from django.db.models import Prefetch

from apps.core.utils.views import PageTitleMixin
from .models import Student, Address
from . import datatables

from django.db import models


class Search(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    title = 'Person'
    subtitle = 'Search'
    template_name = 'student/search.html'

    table_class = datatables.StudentSearchTable
    filterset_class = datatables.StudentSearchFilter

    # A bit complicated, since this search tool also searches on email, phone, address, which are one-to-many relations
    queryset = Student.objects.filter(
        # This is a way of joining in the one-to-many joined fields into the select.
        # We always want the default address data, whether we filter on it or not
        models.Q(address__is_default=True) | models.Q(address__is_default__isnull=True),
    ).annotate(
        # And we want two fields available to the table in the end
        postcode=models.F('address__postcode'),
        line1=models.F('address__line1'),
    ).distinct()

    def get_table_kwargs(self):
        # Hide the email column unless we search by it
        exclude = []
        if not self.request.GET.get('email'):
            exclude.append('email_address')
        return {'exclude': exclude}
