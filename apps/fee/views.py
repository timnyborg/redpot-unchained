from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.views import generic

from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin
from apps.module.models import Module

from . import forms
from .models import Fee


class Create(LoginRequiredMixin, AutoTimestampMixin, SuccessMessageMixin, PageTitleMixin, generic.CreateView):
    template_name = 'core/form.html'
    model = Fee
    form_class = forms.FeeForm
    success_message = 'Fee created: %(description)s (£%(amount).2f)'

    def dispatch(self, request, *args, **kwargs):
        self.module = get_object_or_404(Module, pk=kwargs['module_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.module = self.module
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.module.get_absolute_url() + '#fees'


class Edit(LoginRequiredMixin, AutoTimestampMixin, SuccessMessageMixin, PageTitleMixin, generic.UpdateView):
    template_name = 'core/form.html'
    model = Fee
    form_class = forms.FeeForm
    success_message = 'Fee updated: %(description)s (£%(amount).2f)'

    def get_success_url(self) -> str:
        return self.object.module.get_absolute_url() + '#fees'


class Delete(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    template_name = 'core/delete_form.html'
    model = Fee
    success_message = 'Fee deleted'

    def get_success_url(self) -> str:
        messages.success(self.request, self.success_message)  # DeleteViews don't do this automatically
        return self.object.module.get_absolute_url() + '#fees'
