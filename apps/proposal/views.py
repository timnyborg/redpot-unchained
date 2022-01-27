from django import http
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import generic

from apps.core.utils.views import PageTitleMixin

from . import forms, models


class Edit(PermissionRequiredMixin, PageTitleMixin, SuccessMessageMixin, generic.UpdateView):
    permission_required = 'proposal.add_proposal'
    model = models.Proposal
    form_class = forms.ProposalForm
    template_name = 'core/form.html'
    success_message = 'Changes saved'
    success_url = '#'  # self-redirect, since these have no detail view
    error_message = 'There are errors in the form'

    def form_invalid(self, form) -> http.HttpResponse:
        messages.warning(self.request, self.error_message)
        return super().form_invalid(form)

    # todo: reading list management, image filename modification (why?)


class Delete(PermissionRequiredMixin, PageTitleMixin, generic.DeleteView):
    permission_required = 'proposal.delete_proposal'
    model = models.Proposal
    template_name = 'core/delete_form.html'
    success_url = reverse_lazy('proposal:search')


# todo: remaining proposal views/services
