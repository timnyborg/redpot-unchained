from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.views import generic

from apps.core.utils.views import PageTitleMixin

from . import forms, models, rp_api


class PushPayment(PageTitleMixin, PermissionRequiredMixin, generic.FormView):
    form_class = forms.PushPaymentForm
    template_name = 'core/form.html'
    title = 'Web payments'
    subtitle = 'Push payment'
    permission_required = 'core.finance'

    def form_valid(self, form):
        payment_ref = form.cleaned_data['payment_ref'].strip()
        payment = models.Payment.objects.filter(payment_ref=payment_ref).first()
        if not payment:
            form.add_error('payment_ref', 'Payment with this reference not found')
            return self.form_invalid(form)
        elif payment.status == 'success':
            form.add_error('payment_ref', 'Payment already processed')
            return self.form_invalid(form)

        try:
            api = rp_api.APIClient()
            api.push_payment(payment_ref=payment_ref, wpm_ref=form.cleaned_data['wpm_ref'].strip())
        except rp_api.JSONRPCError as e:
            form.add_error('__all__', str(e))
            return self.form_invalid(form)

        messages.success(self.request, f'Payment {payment_ref} pushed through successfully')
        return redirect(self.request.path)
