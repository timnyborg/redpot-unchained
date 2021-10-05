import django_tables2 as tables
from django_filters.views import FilterView

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin
from apps.enrolment.models import Enrolment

from . import datatables, forms, models


class LimitSearch(LoginRequiredMixin, PageTitleMixin, tables.SingleTableMixin, FilterView):
    model = models.Limit
    template_name = 'booking/limit/search.html'
    table_class = datatables.SearchTable
    filterset_class = datatables.SearchFilter
    subtitle = 'Search'


class CreateLimit(LoginRequiredMixin, AutoTimestampMixin, SuccessMessageMixin, PageTitleMixin, generic.CreateView):
    model = models.Limit
    form_class = forms.LimitForm
    success_message = 'Limit created: %(description)s'
    template_name = 'core/form.html'


class EditLimit(LoginRequiredMixin, AutoTimestampMixin, SuccessMessageMixin, PageTitleMixin, generic.UpdateView):
    model = models.Limit
    template_name = 'booking/limit/edit.html'
    form_class = forms.LimitForm
    success_message = 'Limit updated: %(description)s'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        bookings = self.object.bookings.select_related(
            'enrolment', 'enrolment__module', 'enrolment__qa__student'
        ).order_by('enrolment__qa__student__surname', 'enrolment__qa__student__firstname', 'enrolment__module__code')
        fees = self.object.fees.select_related('module').order_by('module__code')
        return {**context, 'bookings': bookings, 'fees': fees}


class DeleteLimit(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = models.Limit
    template_name = 'core/delete_form.html'

    def get_success_url(self) -> str:
        messages.success(self.request, f'Limit deleted: {self.object.description}')
        return reverse('booking:limit-search')


class CreateAccommodation(
    LoginRequiredMixin, AutoTimestampMixin, SuccessMessageMixin, PageTitleMixin, generic.CreateView
):
    model = models.Accommodation
    template_name = 'core/form.html'
    form_class = forms.AccommodationForm
    success_message = 'Accommodation added'

    def dispatch(self, request, *args, **kwargs) -> http.HttpResponse:
        self.enrolment = get_object_or_404(Enrolment, pk=self.kwargs['enrolment_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form) -> http.HttpResponse:
        form.instance.enrolment = self.enrolment
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.object.enrolment.get_absolute_url() + '#accommodation'


class EditAccommodation(
    LoginRequiredMixin, AutoTimestampMixin, SuccessMessageMixin, PageTitleMixin, generic.UpdateView
):
    model = models.Accommodation
    template_name = 'core/form.html'
    form_class = forms.AccommodationForm
    success_message = 'Accommodation updated'

    def get_success_url(self) -> str:
        return self.object.enrolment.get_absolute_url() + '#accommodation'


class DeleteAccommodation(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = models.Accommodation
    template_name = 'core/delete_form.html'
    subtitle_object = False

    def get_success_url(self) -> str:
        messages.success(self.request, 'Accommodation removed')
        return self.object.enrolment.get_absolute_url() + '#accommodation'


class CreateCatering(LoginRequiredMixin, AutoTimestampMixin, SuccessMessageMixin, PageTitleMixin, generic.CreateView):
    model = models.Catering
    template_name = 'core/form.html'
    form_class = forms.CateringForm
    success_message = 'Catering added'

    def dispatch(self, request, *args, **kwargs) -> http.HttpResponse:
        self.enrolment = get_object_or_404(Enrolment, pk=self.kwargs['enrolment_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        return {**kwargs, 'module': self.enrolment.module}

    def form_valid(self, form) -> http.HttpResponse:
        form.instance.enrolment = self.enrolment
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.object.enrolment.get_absolute_url() + '#catering'


class DeleteCatering(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = models.Catering
    template_name = 'core/delete_form.html'
    subtitle_object = False

    def get_success_url(self) -> str:
        messages.success(self.request, 'Catering removed')
        return self.object.enrolment.get_absolute_url() + '#catering'
