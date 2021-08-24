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

        if self.amendment_type == '6':  # BACS refund - unsupported type.  # Todo - handle this elsewhere - service?
            amendment = models.Amendment.objects.create(
                details='See printed form for details',
                status=2,
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
            1: forms.TransferForm,
            2: forms.AmendmentForm,
            3: forms.RefundForm,
            4: forms.RefundForm,
            5: forms.RefundForm,
            7: forms.RefundForm,
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
        # services.set_narrative(amendment=form.instance)  # noqa
        # services._email_request_status(form.instance)  # noqa
        return super().form_valid(form)

    def get_success_url(self):
        return self.enrolment.get_absolute_url() + '#finances'
