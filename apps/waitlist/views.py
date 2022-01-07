from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.views import generic

from apps.core.utils.views import PageTitleMixin
from apps.student.models import Student
from apps.waitlist import forms, models


class Add(LoginRequiredMixin, SuccessMessageMixin, PageTitleMixin, generic.CreateView):
    model = models.Waitlist
    form_class = forms.WaitlistForm
    subtitle = 'Add'
    success_message = 'Student added to waiting list'
    template_name = 'core/form.html'

    def get_initial(self) -> dict:
        return {'student': get_object_or_404(Student, pk=self.kwargs['student_id'])}

    def get_success_url(self) -> str:
        return self.object.module.get_absolute_url() + '#waitlist'


class Delete(LoginRequiredMixin, PageTitleMixin, generic.DeleteView):
    model = models.Waitlist
    success_message = 'Student removed from waiting list'
    template_name = 'core/delete_form.html'

    def get_success_url(self) -> str:
        messages.success(self.request, self.success_message)
        return self.object.module.get_absolute_url() + '#waitlist'
