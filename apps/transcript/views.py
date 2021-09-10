from django import http
from django.shortcuts import get_object_or_404

from apps.core.utils import strings
from apps.student.models import Student
from apps.transcript.pdfs import transcript_pdf


def pdf(request, student_id: int, level: str, *args, **kwargs):
    student = get_object_or_404(Student, pk=student_id)
    document: str = transcript_pdf(student=student, level=level, header=True)
    filename = (
        'Transcript_%s_%s_%s.pdf' % (level, strings.normalize(student.firstname), strings.normalize(student.surname))
    ).replace(' ', '_')
    return http.HttpResponse(
        document, content_type='application/pdf', headers={'Content-Disposition': f'inline;filename={filename}'}
    )
