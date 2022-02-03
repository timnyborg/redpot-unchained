from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from apps.core.utils.views import PageTitleMixin

from . import models, services


class View(LoginRequiredMixin, PageTitleMixin, generic.DetailView):
    model = models.Application
    template_name = 'application/view.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        return {**context, 'attachments': self.object.attachments.all()}

    def get_subtitle(self) -> str:
        return f'View – {self.object.firstname} {self.object.surname}'


class CreateAndEnrolStudent(LoginRequiredMixin, generic.View):
    """Creates a student record from an application where none exists
    Will be partially rendered obsolete by reworking application form to use core tables (student, email, phone...)
    NB: I've dropped use of match_or_create_student, in expectation of that work.  It can be reintegrated if required
    """

    @transaction.atomic
    def post(self, request, *args, **kwargs) -> http.HttpResponse:
        application = get_object_or_404(models.Application, **self.kwargs)

        if not application.student:
            application.student = services.create_student_from_application(application=application, user=request.user)
            application.save()

        already_enrolled = application.student.get_enrolments(module=application.module).exists()
        if already_enrolled:
            messages.warning(request, 'Student already enrolled on course')
            return redirect(application.student)

        services.enrol_applicant(application=application, user=request.user)
        messages.success(request, 'Student enrolled on course')
        return redirect(application.student)
