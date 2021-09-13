from django import http
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.views import generic

from apps.core.utils import strings
from apps.core.utils.views import PageTitleMixin
from apps.student.models import Student

from . import forms, pdfs, tasks


class PDF(PermissionRequiredMixin, generic.View):
    """Generate a transcript for a single student"""

    permission_required = 'transcript.print'

    def get(self, request, student_id: int, level: str, header: bool = False, *args, **kwargs):
        student = get_object_or_404(Student, pk=student_id)
        document = pdfs.create_transcript(header=header, level=level, student=student)

        filename = strings.normalize(f'Transcript_{level}_{student.firstname}_{student.surname}.pdf').replace(' ', '_')
        return http.HttpResponse(
            document, content_type='application/pdf', headers={'Content-Disposition': f'inline;filename={filename}'}
        )


class CreateBatch(PermissionRequiredMixin, PageTitleMixin, generic.FormView):
    """View to generate a combined pdf of all unprinted transcripts"""

    permission_required = 'transcript.batch print'
    form_class = forms.BatchPrintForm
    template_name = 'transcript/create_batch.html'
    title = 'Transcripts'
    subtitle = 'Create batch'

    def form_valid(self, form) -> http.HttpResponse:
        task = tasks.create_batch.delay(
            header=form.cleaned_data['header'],
            level=form.cleaned_data['level'],
            created_by=self.request.user.username,
        )
        return http.HttpResponse(str(task))  # todo: redirect to a progress view

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        # Get a list of past files
        # todo: get list of past files from a restricted media directory (/transcripts), all .pdfs reverse sorted
        context['history'] = ['fakerecord.pdf']
        return context
