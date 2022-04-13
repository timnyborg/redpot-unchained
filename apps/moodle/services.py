from datetime import datetime
from typing import Iterator

from django.db.models import Max

from apps.module.models import Module
from apps.student.models import Student

from . import models


def next_moodle_id() -> Iterator[int]:
    """Generator which looks up the next ID to be assigned, and provides sequential numbers"""
    # Get largest assigned ID
    previous = models.MoodleID.objects.aggregate(Max('moodle_id'))['moodle_id__max'] or 0
    # We increment the numbers each year, with a year prefix, so it forms a minimum
    minimum = datetime.now().year % 100 * 100000

    val = max(previous + 1, minimum)
    while True:
        yield val
        val += 1


def assign_moodle_id(*, student: Student, created_by: str, first_module_code: str) -> None:
    id_generator = next_moodle_id()
    models.MoodleID.objects.create(
        student=student,
        moodle_id=next(id_generator),
        first_module_code=first_module_code,
        created_by=created_by,
        modified_by=created_by,
    )


def assign_moodle_ids(*, module: Module, created_by: str):
    """
    Acquires and attaches MoodleIDs for students enrolled on a module.
    Marks newly generated IDs with the module code, so the
    report used by TALL can show new passwords and "same as before"
    """

    students = Student.objects.filter(
        qa__enrolment__module=module,
        qa__enrolment__status__takes_place=True,
    ).exclude(moodle_id__id__isnull=False)

    for student in students:
        assign_moodle_id(student=student, first_module_code=module.code, created_by=created_by)

    return len(students)
