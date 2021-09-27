import django_tables2 as tables
from django_filters.views import FilterView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.views import generic

from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin

from . import datatables, forms, models


class Search(LoginRequiredMixin, PageTitleMixin, tables.SingleTableMixin, FilterView):
    queryset = models.Discount.objects.select_related('portfolio')
    table_class = datatables.SearchTable
    filterset_class = datatables.SearchFilter
    subtitle = 'Search'
    template_name = 'core/search.html'


class Create(LoginRequiredMixin, AutoTimestampMixin, SuccessMessageMixin, PageTitleMixin, generic.CreateView):
    model = models.Discount
    form_class = forms.DiscountForm
    template_name = 'core/form.html'
    success_message = 'Discount created – please assign recipients'

    def get_success_url(self):
        return reverse('discount:assign', args=[self.object.id])


class Edit(LoginRequiredMixin, AutoTimestampMixin, SuccessMessageMixin, PageTitleMixin, generic.UpdateView):
    model = models.Discount
    form_class = forms.DiscountForm
    template_name = 'core/form.html'
    success_message = 'Discount updated'

    def get_success_url(self):
        return reverse('discount:search') + f'?code={self.object.code}'
