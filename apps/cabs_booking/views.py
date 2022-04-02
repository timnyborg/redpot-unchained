from datetime import date

from django import forms, http
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import QuerySet
from django.shortcuts import redirect
from django.views import generic

from apps.core.utils.views import PageTitleMixin
from apps.module.models import Module

from . import tasks

WEEKLY_PORTFOLIO = 32


class SubmitForm(forms.Form):
    submit_label = 'Make bookings'


class AnnualWeeklyClassBookings(PermissionRequiredMixin, PageTitleMixin, generic.FormView):
    template_name = 'cabs_bookings/form.html'
    form_class = SubmitForm
    title = 'CABS'
    subtitle = 'Bulk weekly classes bookings'
    permission_required = 'module.upload_to_cabs'

    def get_queryset(self) -> QuerySet[Module]:
        return Module.objects.filter(
            portfolio_id=WEEKLY_PORTFOLIO,
            room__isnull=False,
            room_setup__isnull=False,
            start_time__isnull=False,
            end_time__isnull=False,
            start_date__gt=date.today(),
            end_date__isnull=False,
            is_cancelled=False,
            cabs_booking__isnull=True,  # No previous bookings
        )

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        return {**context, 'module_count': self.get_queryset().count()}

    def form_valid(self, form) -> http.HttpResponse:
        module_ids = list(self.get_queryset().values_list('id', flat=True))
        task = tasks.batch_cabs_module_bookings.delay(module_ids=module_ids)
        return redirect('task:progress', task_id=task.id)
