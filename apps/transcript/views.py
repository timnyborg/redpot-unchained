from datetime import datetime

from django import http
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.views import generic

from apps.core.utils import postal, strings
from apps.student.models import Student

from . import pdfs, services


class PDF(PermissionRequiredMixin, generic.View):
    """Generate a"""

    permission_required = 'transcript.print'

    def get(self, request, student_id: int, level: str, *args, **kwargs):
        student = get_object_or_404(Student, pk=student_id)
        enrolments = services.get_enrolments_for_transcript(student=student, level=level)
        address = student.get_default_address()
        address_lines = postal.format_address(address) if address else []
        document: str = pdfs.transcript(
            student=student, address_lines=address_lines, enrolments=list(enrolments), level=level, header=True
        )
        enrolments.filter(transcript_date__isnull=True).update(transcript_date=datetime.now())

        filename = strings.normalize(f'Transcript_{level}_{student.firstname}_{student.surname}.pdf').replace(' ', '_')
        return http.HttpResponse(
            document, content_type='application/pdf', headers={'Content-Disposition': f'inline;filename={filename}'}
        )
