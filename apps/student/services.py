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
