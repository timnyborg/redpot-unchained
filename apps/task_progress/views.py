from celery_progress.views import get_progress

from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from apps.core.utils.views import PageTitleMixin


class ViewProgress(LoginRequiredMixin, PageTitleMixin, generic.TemplateView):
    """Renders celery task progress"""

    template_name = 'task_progress/view_progress.html'
    title = 'Task'
    subtitle = 'Progress'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data()
        return {**context, 'task_id': self.kwargs['task_id']}


class Status(LoginRequiredMixin, generic.View):
    """A wrapper around celery-progress' get_progress view, to add authentication"""

    def get(self, request, task_id: str, *args, **kwargs) -> http.HttpResponse:
        return get_progress(request, task_id=task_id)
