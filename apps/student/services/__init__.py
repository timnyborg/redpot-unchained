from __future__ import annotations

import itertools

from .. import models
from . import merge


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
    multipliers = itertools.cycle([1, 3, 7, 9])
    checkdigit = (10 - sum(int(a) * b for a, b in zip(head, multipliers))) % 10
    husid = head + str(checkdigit)

    return int(husid)


def _generate_sid(*, academic_year: int, seed: int, ukprn: int = 10007774):
    """Produce a valid SID from an academic year and seed value, according to the HESA guidance
    See https://www.hesa.ac.uk/collection/student/datafutures/a/student_sid
    Identical to husid production, but the 4 digit institution code has been replaced with 8 digits for data futures.
    """

    # First 14 digits are: two year digits, the institution (ukprn), and the seed (zero padded to 6 digits)
    year_digits = str(academic_year)[-2:]
    seed_digits = str(seed).zfill(6)
    head = year_digits + str(ukprn) + seed_digits

    # Get the checksum (weighted product of 14 digits -> summed -> last digit subtracted from 10).
    multipliers = itertools.cycle([1, 3, 7, 9])
    checkdigit = (10 - sum(int(a) * b for a, b in zip(head, multipliers))) % 10
    husid = head + str(checkdigit)

    return int(husid)


EMPTY_ATTRIBUTE_VALUES: dict[str, list] = {
    'birthdate': [],
    'gender': [],
    'nationality': [models.NOT_KNOWN_NATIONALITY],
    'domicile': [models.NOT_KNOWN_DOMICILE],
    'ethnicity': [models.NOT_KNOWN_ETHNICITY],
    'religion_or_belief': [models.NOT_KNOWN_RELIGION],
    'highest_qualification': ['X06'],  # todo: replace with enum
}


def missing_student_data(*, student: models.Student) -> list[str]:
    """Returns a list of fields lacking values (null or Not known)"""
    # Todo: append _id once religion & highest qual models are implemented
    empty_fields = []
    for attribute, values in EMPTY_ATTRIBUTE_VALUES.items():
        fieldname = attribute
        # for foreign keys, we need to check the _id
        if hasattr(student, attribute + '_id'):
            fieldname += '_id'
        value = getattr(student, fieldname)
        # plain values
        if value in [None] + values:
            empty_fields.append(attribute)

    return empty_fields


def supplement_student_data(*, student: models.Student, **kwargs) -> None:
    """Updates the attributes of a student record"""
    for field, value in kwargs.items():
        if not models.Student._meta.get_field(field):
            raise AttributeError(f"Student model doesn't have a field '{field}'")
        setattr(student, field, value)
    student.full_clean()
    student.save()
