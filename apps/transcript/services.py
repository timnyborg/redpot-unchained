from django.db import models

from apps.enrolment.models import Enrolment
from apps.student.models import Student


def get_enrolments_for_transcript(*, student: Student, level: str) -> models.QuerySet[Enrolment]:
    """Gets"""
    level_map = {
        'undergraduate': [61],
        'postgraduate': [62, 63],
    }
    return (
        Enrolment.objects.filter(
            qa__student=student,
            status_id__in=(10, 11),  # confirmed for credit
            result_id__in=('A', '1'),  # Passed.  'A' is historical
            qa__programme__qualification_id__in=level_map[level],
            points_awarded__gt=0,
        )
        .exclude(
            module__start_date__isnull=True,  # Filter out old incomplete records
        )
        .exclude(
            module__end_date__isnull=True,  # Filter out old incomplete records
        )
        .select_related('module', 'module__points_level')
        .order_by('-module__start_date', 'module__code')
    )
