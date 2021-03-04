from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from apps.core.utils.views import PageTitleMixin
from apps.tutor.models import TutorModule

from . import forms


class Extras(PageTitleMixin, SuccessMessageMixin, SingleObjectMixin, FormView):
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
            user=self.request.user
        )
        return super().form_valid(form)
