from datetime import datetime

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from apps.core.utils.views import PageTitleMixin
from apps.enrolment.models import Enrolment

from . import forms, models, services


class Create(LoginRequiredMixin, PageTitleMixin, SuccessMessageMixin, generic.CreateView):
    success_message = 'Request submitted for approval'
    title = 'Finance change request'
    template_name = 'core/form.html'

    def dispatch(self, request, *args, **kwargs):
        self.enrolment = get_object_or_404(Enrolment, pk=self.kwargs['enrolment_id'])
        self.amendment_type = get_object_or_404(models.AmendmentType, pk=self.kwargs['type_id'])

        if self.amendment_type == models.AmendmentTypes.OTHER_REFUND:
            # Refunds requiring paper forms (BACS?) # Todo - handle this elsewhere - service?  Standalone view?
            amendment = models.Amendment.objects.create(
                details='See printed form for details',
                status=models.AmendmentStatuses.APPROVED,
                raised_by=request.user.username,
                raised_on=datetime.now(),
                approved_by=request.user.username,
                approved_on=datetime.now(),
            )
            services.set_narrative(amendment=amendment)
            return redirect(settings.STATIC_URL + 'templates/bacs_refund_form_r12.xls')
        return super().dispatch(request, *args, **kwargs)

    def get_subtitle(self) -> str:
        return f'New – {self.enrolment.qa.student} on {self.enrolment.module}'

    def get_form_class(self) -> ModelForm:
        form_classes = {
            models.AmendmentTypes.TRANSFER: forms.TransferForm,
            models.AmendmentTypes.AMENDMENT: forms.AmendmentForm,
            models.AmendmentTypes.ONLINE_REFUND: forms.RefundForm,
            models.AmendmentTypes.CREDIT_CARD_REFUND: forms.RefundForm,
            models.AmendmentTypes.RCP_REFUND: forms.RefundForm,
            models.AmendmentTypes.BANK_REFUND: forms.RefundForm,
        }
        return form_classes[self.amendment_type.id]

    def get_initial(self):
        return {
            'type': self.amendment_type,
            'enrolment': self.enrolment,
        }

    def form_valid(self, form):
        form.instance.requested_on = datetime.now()
        form.instance.requested_by = self.request.user.username
        form.instance.narrative = services.get_narrative(amendment=form.instance)
        # services._email_request_status(form.instance)  # noqa
        return super().form_valid(form)

    def get_success_url(self):
        return self.enrolment.get_absolute_url() + '#finances'
