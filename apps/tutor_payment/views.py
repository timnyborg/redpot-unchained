from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import generic
from django.views.generic.detail import SingleObjectMixin

from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin
from apps.tutor.models import TutorModule

from . import datatables, forms, models


class Create(PermissionRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.CreateView):
    model = models.TutorFee
    permission_required = 'tutor_payment.raise'
    template_name = 'core/form.html'
    form_class = forms.CreateForm

    def dispatch(self, request, *args, **kwargs):
        # get the parent record for generating the title and adding to the child record on form submission
        self.tutor_module = get_object_or_404(TutorModule, pk=self.kwargs['tutor_module_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.tutor_module = self.tutor_module
        form.instance.raised_by = self.request.user.username
        return super().form_valid(form)

    def get_subtitle(self):
        return f'New – {self.tutor_module}'

    def get_success_url(self):
        if url_has_allowed_host_and_scheme(self.request.GET.get('next'), allowed_hosts=None):
            return self.request.GET.get('next')
        return self.tutor_module.get_absolute_url() + '#payments'


class Edit(LoginRequiredMixin, SuccessMessageMixin, PageTitleMixin, AutoTimestampMixin, generic.UpdateView):
    model = models.TutorFee
    form_class = forms.EditForm
    success_message = 'Record updated'
    template_name = 'core/form.html'
    subtitle_object = False

    def can_edit(self):
        if self.object.status_id == models.Statuses.RAISED:
            return (
                self.request.user.has_perm('tutor_payment.raise')
                and self.object.raised_by == self.request.user.username.lower()
            )
        if self.object.status_id == models.Statuses.APPROVED:
            return self.request.user.has_perm('tutor_payment.approve')
        if self.object.status_id == models.Statuses.TRANSFERRED:
            return self.request.user.has_perm('tutor_payment.transfer')
        return False

    def get_form_kwargs(self):
        # If not allowed to edit, display instead. should this be elsewhere?
        if not self.can_edit():
            return redirect(self.object.get_absolute_url())

        kwargs = super().get_form_kwargs()
        kwargs['editable_status'] = self.request.user.has_perm('tutor_payment.transfer')
        return kwargs

    def get_success_url(self):
        if url_has_allowed_host_and_scheme(self.request.GET.get('next'), allowed_hosts=None):
            return self.request.GET.get('next')
        return self.object.tutor_module.get_absolute_url() + '#payments'


class Extras(PageTitleMixin, SuccessMessageMixin, SingleObjectMixin, LoginRequiredMixin, generic.FormView):
    template_name = 'tutor_payment/extras.html'
    form_class = forms.ExtrasForm
    model = TutorModule
    title = 'Tutor Payment'
    subtitle = 'Extras'
    success_message = 'Fees added'

    def dispatch(self, request, *args, **kwargs):
        # Set object so we can use it in several places
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url() + '#fees'

    def form_valid(self, form):
        form.create_record(
            tutor_module=self.object,
            user=self.request.user,
        )
        return super().form_valid(form)


class Search(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    title = 'Tutor payment'
    subtitle = 'Search'
    template_name = 'core/search.html'

    table_class = datatables.SearchTable
    filterset_class = datatables.SearchFilter
