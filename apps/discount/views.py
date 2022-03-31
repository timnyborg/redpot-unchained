import django_tables2 as tables
from django_filters.views import FilterView

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views import generic

from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin

from . import datatables, forms, models


class Search(PermissionRequiredMixin, PageTitleMixin, tables.SingleTableMixin, FilterView):
    permission_required = 'discount.view_discount'
    queryset = models.Discount.objects.select_related('portfolio')
    table_class = datatables.SearchTable
    filterset_class = datatables.SearchFilter
    subtitle = 'Search'
    template_name = 'core/search.html'


class Create(PermissionRequiredMixin, AutoTimestampMixin, SuccessMessageMixin, PageTitleMixin, generic.CreateView):
    permission_required = 'discount.add_discount'
    model = models.Discount
    form_class = forms.DiscountForm
    template_name = 'core/form.html'
    success_message = 'Discount %(code)s created – please assign recipients'

    def get_success_url(self):
        return reverse('discount:assign', args=[self.object.id])


class Edit(PermissionRequiredMixin, AutoTimestampMixin, SuccessMessageMixin, PageTitleMixin, generic.UpdateView):
    permission_required = 'discount.change_discount'
    model = models.Discount
    form_class = forms.DiscountForm
    template_name = 'core/form.html'
    success_message = 'Discount %(code)s updated'

    def get_success_url(self):
        return reverse('discount:search') + f'?code={self.object.code}'


class Delete(PermissionRequiredMixin, PageTitleMixin, generic.DeleteView):
    permission_required = 'discount.delete_discount'
    model = models.Discount
    form_class = forms.DiscountForm
    template_name = 'core/delete_form.html'
    success_url = reverse_lazy('discount:search')

    def get_success_url(self) -> str:
        messages.success(self.request, f'Discount {self.object.code} deleted')
        return self.success_url
