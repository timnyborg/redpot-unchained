from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.views import generic

from apps.core.utils.views import AutoTimestampMixin, PageTitleMixin
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
