from datetime import date

from django import forms, http
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from apps.core.utils.views import PageTitleMixin
from apps.module.models import Module

from . import services, tasks

WEEKLY_PORTFOLIO = 32


class SubmitForm(forms.Form):
    submit_label = 'Make bookings'


class AnnualWeeklyClassBookings(PermissionRequiredMixin, PageTitleMixin, generic.FormView):
    """Create bookings for all future weekly classes"""

    template_name = 'cabs_bookings/annual_weekly_class_bookings.html'
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


class CreateModuleBookings(PermissionRequiredMixin, PageTitleMixin, generic.FormView):
    """Create bookings for a single module"""

    template_name = 'cabs_bookings/create_module_bookings.html'
    form_class = SubmitForm
    title = 'CABS'
    subtitle = 'Create module bookings'
    permission_required = 'module.upload_to_cabs'
    model = Module

    def dispatch(self, request, *args, **kwargs) -> http.HttpResponse:
        self.object = get_object_or_404(Module, **self.kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        return {
            **context,
            'module': self.object,
            'equipment': self.object.equipment.all(),
            'previous_bookings': self.object.cabs_bookings.all(),
        }

    def form_valid(self, form) -> http.HttpResponse:
        module = self.object
        if (
            not module.start_date
            and module.start_time
            and module.end_date
            and module.end_time
            and module.room_id
            and module.room_setup
        ):
            form.add_error('', 'The module must have start and end dates and times, a room, and room setup.')
            return self.form_invalid(form)

        booking = services.create_module_bookings(module=self.object)
        messages.success(
            self.request,
            f'{booking.confirmed} confirmed and {booking.provisional} provisional '
            'bookings were successfully created in CABS',
        )
        return redirect(module)
