from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from apps.core.utils.views import AutoTimestampMixin, DeletionFailedMessageMixin, PageTitleMixin
from apps.student.models import Student

from . import forms, models


class Create(LoginRequiredMixin, SuccessMessageMixin, AutoTimestampMixin, PageTitleMixin, generic.CreateView):
    model = models.QualificationAim
    template_name = 'core/form.html'
    form_class = forms.CreateForm
    success_message = 'Student added to programme'

    def dispatch(self, request, *args, **kwargs):
        # get the parent record for generating the title and adding to the child record on form submission
        self.student = get_object_or_404(Student, pk=self.kwargs['student_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.student = self.student
        return super().form_valid(form)

    def get_subtitle(self):
        return f'New – {self.student}'


class View(LoginRequiredMixin, PageTitleMixin, generic.DetailView):
    queryset = models.QualificationAim.objects.select_related('entry_qualification', 'programme')
    template_name = 'qualification_aim/view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrolments = self.object.enrolments.select_related('module', 'status', 'result').order_by(
            '-module__start_date', 'module__code'
        )
        return {
            **context,
            'student': self.object.student,
            'enrolments': enrolments,
        }


class Edit(LoginRequiredMixin, AutoTimestampMixin, SuccessMessageMixin, PageTitleMixin, generic.UpdateView):
    model = models.QualificationAim
    form_class = forms.EditForm
    template_name = 'core/form.html'
    success_message = 'Qualification aim updated'


class Delete(LoginRequiredMixin, DeletionFailedMessageMixin, PageTitleMixin, generic.DeleteView):
    model = models.QualificationAim
    template_name = 'core/delete_form.html'

    def get_success_url(self) -> str:
        return self.object.student.get_absolute_url()


class EditCertHEMarks(LoginRequiredMixin, AutoTimestampMixin, SuccessMessageMixin, PageTitleMixin, generic.UpdateView):
    model = models.CertHEMarks
    form_class = forms.CertHEMarksForm
    template_name = 'core/form.html'
    success_message = 'CertHE marks updated'

    def dispatch(self, request, *args, **kwargs):
        self.qualification_aim = get_object_or_404(models.QualificationAim, pk=self.kwargs['qa_id'])
        if not self.qualification_aim.programme.is_certhe:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        # Create the child record if it doesn't exist.
        # Not sure why we do it this way instead of having a CREATE button
        try:
            return self.qualification_aim.certhe_marks
        except models.CertHEMarks.DoesNotExist:
            return models.CertHEMarks.objects.create(qualification_aim=self.qualification_aim)

    def get_subtitle(self):
        return f'Edit – {self.qualification_aim.student}'

    def get_success_url(self) -> str:
        return self.qualification_aim.get_absolute_url()
