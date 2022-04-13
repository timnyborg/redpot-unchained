from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin
from apps.module.models import Module
from apps.student.models import Student

from . import forms, models, services


class Create(LoginRequiredMixin, AutoTimestampMixin, PageTitleMixin, SuccessMessageMixin, generic.CreateView):
    model = models.MoodleID
    form_class = forms.CreateMoodleIDForm
    template_name = 'core/form.html'

    def get_initial(self) -> dict:
        return {'student': get_object_or_404(Student, pk=self.kwargs['student_id'])}

    def get_success_url(self) -> str:
        return self.object.student.get_absolute_url() + '#other_ids'


class Edit(LoginRequiredMixin, PageTitleMixin, AutoTimestampMixin, SuccessMessageMixin, generic.UpdateView):
    model = models.MoodleID
    template_name = 'core/form.html'
    form_class = forms.MoodleIDForm


class Delete(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = models.MoodleID
    template_name = 'core/delete_form.html'

    def get_success_url(self) -> str:
        messages.success(self.request, 'Moodle ID deleted')
        return self.object.student.get_absolute_url() + '#other_ids'


class AssignToModule(LoginRequiredMixin, SuccessMessageMixin, generic.View):
    """Generates moodle IDs for all a module's students, redirecting back to the module page"""

    def post(self, request, module_id: int) -> http.HttpResponse:
        module = get_object_or_404(Module, pk=module_id)
        count = services.assign_moodle_ids(module=module, created_by=request.user.username)
        messages.success(request, f'{count} moodle ID(s) generated')
        return redirect(module)
