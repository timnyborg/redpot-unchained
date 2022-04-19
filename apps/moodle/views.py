from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import EmailMultiAlternatives
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views import generic
from django.views.generic import FormView

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


class RequestSite(LoginRequiredMixin, SuccessMessageMixin, PageTitleMixin, FormView):
    form_class = forms.RequestSiteForm
    template_name = 'core/form.html'
    title = 'Moodle'
    subtitle = 'Request site'
    success_message = 'Site request submitted'

    def dispatch(self, request, *args, **kwargs) -> http.HttpResponse:
        self.module = get_object_or_404(Module, pk=self.kwargs['module_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self) -> dict:
        return {
            'title': self.module.title,
            'start_date': self.module.start_date,
            'access_start_date': self.module.start_date,
            'end_date': self.module.end_date,
            'access_end_date': self.module.end_date,
            'email': self.module.email,
            'admin': self.request.user.get_full_name(),
        }

    def form_valid(self, form) -> http.HttpResponse:
        message = render_to_string(
            'moodle/email/request_site.html',
            context={'module': self.module, **form.cleaned_data},
        )
        mail = EmailMultiAlternatives(
            subject=f'Moodle course setup request:{self.module.title} ({self.module.code})',
            body=strip_tags(message),
            to=[settings.SUPPORT_EMAIL if settings.DEBUG else 'tallithelp@conted.ox.ac.uk'],
            cc=None if settings.DEBUG else [form.cleaned_data['email']],
            from_email=form.cleaned_data['email'],
        )
        mail.attach_alternative(message, 'text/html')
        mail.send()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.module.get_absolute_url()


class AddStudents(PageTitleMixin, generic.TemplateView):
    template_name = 'moodle/add_students.html'
    title = 'Moodle'
    subtitle = 'Add people to a site'

    def dispatch(self, request, *args, **kwargs):
        self.module = get_object_or_404(Module, pk=self.kwargs['module_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_students(self) -> QuerySet[Student]:
        return Student.objects.filter(qa__enrolment__module=self.module, qa__enrolment__status__takes_place=True)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        return {**context, 'module': self.module, 'students': self.get_students()}

    def post(self, request, **kwargs) -> http.HttpResponse:
        content = services.generate_student_spreadsheet(module=self.module, students=self.get_students())
        return http.HttpResponse(
            content=content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename="moodle_students_{self.module.code}.xlsx"'},
        )
