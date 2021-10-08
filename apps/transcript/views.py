from django import http
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from apps.core.utils import strings
from apps.core.utils.views import PageTitleMixin
from apps.student.models import Student

from . import forms, pdfs, tasks


class PDF(PermissionRequiredMixin, generic.View):
    """Generate a transcript for a single student"""

    permission_required = 'transcript.print'

    def get(self, request, student_id: int, level: str, header: bool = False, *args, **kwargs) -> http.HttpResponse:
        student = get_object_or_404(Student, pk=student_id)
        document = pdfs.create_transcript(header=header, level=level, student=student)

        filename = strings.normalize(f'Transcript_{level}_{student.firstname}_{student.surname}.pdf').replace(' ', '_')
        return http.HttpResponse(
            document, content_type='application/pdf', headers={'Content-Disposition': f'inline;filename={filename}'}
        )


class CreateBatch(PermissionRequiredMixin, PageTitleMixin, generic.FormView):
    """View to generate a combined pdf of all unprinted transcripts"""

    permission_required = 'transcript.batch_print'
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
        return redirect('task:progress', task_id=task.id)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        # Get a list of past files
        file_path = settings.PROTECTED_MEDIA_ROOT / 'transcripts'
        file_path.mkdir(parents=True, exist_ok=True)

        context['history'] = sorted([file.stem + file.suffix for file in file_path.iterdir()], reverse=True)
        return context


class ViewBatch(PermissionRequiredMixin, generic.View):
    permission_required = 'transcript.batch_print'

    def get(self, request, filename: str, *args, **kwargs) -> http.HttpResponse:
        path = settings.PROTECTED_MEDIA_URL + 'transcripts/' + filename
        return http.HttpResponse(content_type='', headers={'X-Accel-Redirect': path})
