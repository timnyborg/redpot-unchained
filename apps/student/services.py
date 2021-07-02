from datetime import datetime
from typing import Iterator, Optional

from django.db.models import Max

from . import models


def next_husid(academic_year: int) -> int:
    """Allocates and returns the next HUSID for a given academic year"""
    if not 1990 < academic_year <= 2090:
        raise ValueError('academic_year must be between 1991 and 2090')

    record, _ = models.NextHUSID.objects.get_or_create(year=academic_year)
    husid = _generate_husid(academic_year=academic_year, seed=record.next)
    record.next += 1
    record.save()

    return husid


def _generate_husid(*, academic_year: int, seed: int) -> int:
    """Produce a valid HUSID from an academic year and seed value, according to the HESA guidance
    See https://www.hesa.ac.uk/collection/c08053/e/husid
    """

    # First 12 digits are: two year digits, the institution (1156), and the seed (zero padded to 6 digits)
    year_digits = str(academic_year)[-2:]
    seed_digits = str(seed).zfill(6)
    head = year_digits + '1156' + seed_digits

    # Get the checksum (weighted product of 12 digits -> summed -> last digit subtracted from 10).
    multipliers = [1, 3, 7, 9] * 3
    checkdigit = (10 - sum(int(a) * b for a, b in zip(head, multipliers))) % 10
    husid = head + str(checkdigit)

    return int(husid)


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


def assign_moodle_id(*, student: models.Student, created_by: str, first_module_code: Optional[str] = None) -> None:
    id_generator = next_moodle_id()
    models.MoodleID.objects.create(
        student=student,
        moodle_id=next(id_generator),
        first_module_code=first_module_code,
        created_by=created_by,
        modified_by=created_by,
    )
