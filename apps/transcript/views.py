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
