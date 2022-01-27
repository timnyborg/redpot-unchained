from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views import generic

from apps.core.utils.views import PageTitleMixin

from . import forms, models


class Edit(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, generic.UpdateView):
    model = models.Proposal
    form_class = forms.ProposalForm
    template_name = 'core/form.html'
    success_message = 'Changes saved'
    success_url = '#'  # self-redirect, since these have no detail view

    # todo: reading list management, image filename modification (why?)


# todo: remaining proposal views/services
