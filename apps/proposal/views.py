from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.urls import reverse_lazy
from django.views import generic

from apps.core.utils.views import AutoTimestampMixin, ErrorBannerMixin, PageTitleMixin

from . import datatables, forms, models, services


class Edit(
    PermissionRequiredMixin,
    ErrorBannerMixin,
    AutoTimestampMixin,
    PageTitleMixin,
    SuccessMessageMixin,
    generic.UpdateView,
):
    permission_required = 'proposal.add_proposal'
    model = models.Proposal
    form_class = forms.EditProposalForm
    template_name = 'proposal/form.html'
    success_message = 'Changes saved'
    success_url = '#'  # self-redirect, since these have no detail view

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        return {
            **context,
            'statuses': models.Statuses,
            'books': self.object.module.books.order_by('type', 'title'),
        }


class Delete(PermissionRequiredMixin, PageTitleMixin, generic.DeleteView):
    permission_required = 'proposal.delete_proposal'
    model = models.Proposal
    template_name = 'core/delete_form.html'
    success_url = reverse_lazy('proposal:search')

    def get_success_url(self) -> str:
        messages.success(self.request, 'Proposal deleted')
        return super().get_success_url()


class Search(PermissionRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    permission_required = 'proposal.view_proposal'
    model = models.Proposal
    template_name = 'proposal/search.html'
    table_class = datatables.SearchTable
    filterset_class = datatables.SearchFilter
    subtitle = 'Search'


class New(PermissionRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.FormView):
    permission_required = 'proposal.add_proposal'
    model = models.Proposal
    template_name = 'core/form.html'
    form_class = forms.NewProposalForm
    subtitle = 'New'
    success_message = 'Proposal created'

    @transaction.atomic
    def form_valid(self, form) -> http.HttpResponse:
        tutor_module = form.cleaned_data['tutor_module']
        language_course = form.cleaned_data['limited']
        self.proposal = models.Proposal.objects.create(
            module=tutor_module.module,
            tutor=tutor_module.tutor,
            dos=form.cleaned_data['dos'],
            due_date=form.cleaned_data['due_date'],
            limited=language_course,
            field_trips=models.FieldTripChoices.NONE if language_course else None,  # todo: what's the point of this
            created_by=self.request.user.username,
            modified_by=self.request.user.username,
        )
        services.populate_from_module(proposal=self.proposal)
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.proposal.get_edit_url()


class ViewMessages(PermissionRequiredMixin, PageTitleMixin, generic.DetailView):
    model = models.Proposal
    permission_required = 'proposal.view_proposal'
    template_name = 'proposal/view_messages.html'
    subtitle = 'Message history'


class Summary(PermissionRequiredMixin, generic.DetailView):
    model = models.Proposal
    permission_required = 'proposal.view_proposal'
    template_name = 'proposal/summary.html'

    def get_context_data(self, **kwargs) -> dict:
        return services.get_summary_context(proposal=self.object)
