from urllib.parse import urlencode

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.detail import SingleObjectMixin

from apps.core.utils.urls import next_url_if_safe
from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin
from apps.tutor.models import TutorModule

from . import datatables, forms, models, services


class Create(PermissionRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.CreateView):
    model = models.TutorPayment
    permission_required = 'tutor_payment.raise'
    template_name = 'core/form.html'
    form_class = forms.PaymentForm

    def dispatch(self, request, *args, **kwargs):
        # get the parent record for generating the title and adding to the child record on form submission
        self.tutor_module = get_object_or_404(TutorModule, pk=self.kwargs['tutor_module_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.tutor_module = self.tutor_module
        form.instance.raised_by = self.request.user
        return super().form_valid(form)

    def get_subtitle(self):
        return f'New – {self.tutor_module}'

    def get_success_url(self) -> str:
        return next_url_if_safe(self.request) or self.tutor_module.get_absolute_url() + '#payments'


class Edit(LoginRequiredMixin, SuccessMessageMixin, PageTitleMixin, AutoTimestampMixin, generic.UpdateView):
    model = models.TutorPayment
    form_class = forms.PaymentForm
    success_message = 'Record updated'
    template_name = 'core/form.html'
    subtitle_object = False

    def get_form_kwargs(self):
        # If not allowed to edit, display instead. should this be elsewhere?
        if not self.object.user_can_edit(self.request.user):
            return redirect(self.object.get_absolute_url())

        kwargs = super().get_form_kwargs()
        kwargs['editable_status'] = self.request.user.has_perm('tutor_payment.transfer')
        return kwargs

    def get_success_url(self) -> str:
        return next_url_if_safe(self.request) or self.object.tutor_module.get_absolute_url() + '#payments'


class Delete(PermissionRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = models.TutorPayment
    template_name = 'core/delete_form.html'
    success_url = reverse_lazy('tutor-payment:search')
    subtitle = 'Delete'
    subtitle_object = False

    def has_permission(self) -> bool:
        return self.get_object().user_can_edit(self.request.user)


class Search(LoginRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    title = 'Tutor payment'
    subtitle = 'Search'
    template_name = 'core/search.html'

    table_class = datatables.SearchTable
    filterset_class = datatables.SearchFilter


class Approve(PermissionRequiredMixin, PageTitleMixin, SingleTableMixin, FilterView):
    """List of payments assigned to the current user"""

    model = models.TutorPayment
    permission_required = 'tutor_payment.approve'
    template_name = 'tutor_payment/approve.html'
    subtitle = 'Approve'

    table_class = datatables.ApprovalTable
    filterset_class = datatables.ApprovalFilter

    def get_queryset(self) -> QuerySet:
        return self.request.user.approver_payments.filter(status=models.Statuses.RAISED).select_related(
            'type', 'tutor_module__tutor__student', 'tutor_module__module'
        )

    def post(self, request, urllib=None, *args, **kwargs) -> http.HttpResponse:
        ids: list[str] = request.POST.getlist('payment')
        int_ids: list[int] = [int(i) for i in ids if i.isnumeric()]
        update_count = services.approve_payments(payment_ids=int_ids, username=request.user.username)
        message_method = messages.success if update_count else messages.error
        message_method(request, f"{update_count or 'No'} payments approved")
        return redirect(self.request.path_info + '?' + urlencode(self.request.GET))  # preserve filtering


class Extras(PageTitleMixin, SuccessMessageMixin, SingleObjectMixin, LoginRequiredMixin, generic.FormView):
    template_name = 'tutor_payment/extras.html'
    form_class = forms.ExtrasForm
    model = TutorModule
    title = 'Tutor Payment'
    subtitle = 'Extras'
    success_message = 'Payments added'

    def dispatch(self, request, *args, **kwargs):
        # Set object so we can use it in several places
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return self.object.get_absolute_url() + '#payments'

    def form_valid(self, form):
        form.create_record(
            tutor_module=self.object,
            user=self.request.user,
        )
        return super().form_valid(form)
