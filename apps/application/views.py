from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from apps.core.utils.views import PageTitleMixin

from . import models


class View(LoginRequiredMixin, PageTitleMixin, generic.DetailView):
    model = models.Application
    template_name = 'application/view.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        return {**context, 'attachments': self.object.attachments.all()}

    def get_subtitle(self) -> str:
        return f'View – {self.object.firstname} {self.object.surname}'
