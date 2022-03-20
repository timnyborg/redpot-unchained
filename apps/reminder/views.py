from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from apps.core.utils.views import PageTitleMixin
from apps.module.models import Module

from . import services


class Preview(LoginRequiredMixin, PageTitleMixin, generic.DetailView):
    model = Module
    template_name = 'reminder/preview.html'
    title = 'Course reminder'
    subtitle = 'Preview'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        preview = services.render_reminder(module=self.object, first_name='Example Student')
        return {**context, 'preview': preview}
