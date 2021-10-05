from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.views import generic

from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin
from apps.enrolment.models import Enrolment

from . import forms, models


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
