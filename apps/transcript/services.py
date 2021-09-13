from django.db import models

from apps.enrolment.models import Enrolment
from apps.student.models import Student


def get_enrolments_for_transcript(*, student: Student, level: str) -> models.QuerySet[Enrolment]:
    """Gets the enrolments to print for a given student transcript"""
    level_map = {
        'undergraduate': [61],
        'postgraduate': [62, 63],
    }
    return (
        Enrolment.objects.transcript_printable()
        .filter(
            qa__student=student,
            qa__programme__qualification_id__in=level_map[level],
        )
        .select_related('module', 'module__points_level')
        .order_by('-module__start_date', 'module__code')
    )
