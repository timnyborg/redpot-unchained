from __future__ import annotations

from datetime import datetime
from typing import Any, Iterator

from django.db import transaction
from django.db.models import Max

from apps.tutor.models import Tutor

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


def assign_moodle_id(*, student: models.Student, created_by: str, first_module_code: str) -> None:
    id_generator = next_moodle_id()
    models.MoodleID.objects.create(
        student=student,
        moodle_id=next(id_generator),
        first_module_code=first_module_code,
        created_by=created_by,
        modified_by=created_by,
    )


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


class CannotMergeError(Exception):
    """Indicates that business logic disallows merging two student records"""


def _order_by_husid(student: models.Student) -> tuple:
    """Order husids by priority: Oldest (99 before 00), and student (integer) before enquiry (null)"""
    year = (student.husid or 0) // 10 ** 11  # e.g. 95, 00, 21
    return student.husid is None, year < 90, year


def merge_multiple_students(students: list[models.Student]) -> dict:
    """Merge multiple students, their ids passed in a list"""
    target, *sources = sorted(students, key=_order_by_husid)

    results = {'target': target.id, 'merges': []}

    for source in sources:
        merge_result = {
            # todo: why?
            'id': source.id,
            'name': str(source),
            'husid': source.husid,
        }

        try:
            merge_students(source=source, target=target)
            merge_result['error'] = False
        except CannotMergeError as error:
            merge_result['error'] = error

        results['merges'].append(merge_result)

    return results


@transaction.atomic
def merge_students(*, source: models.Student, target: models.Student):
    # todo: docstring
    # todo: refactor into testable sub-functions
    if hasattr(source, 'tutor') and hasattr(target, 'tutor'):
        raise CannotMergeError("Both records are tutors.  This can't be handled yet.")
    if source.sits_id and target.sits_id and source.sits_id != target.sits_id:
        raise CannotMergeError('Conflicting SITS IDs')

    create_merge_archive_record(source=source, target=target)

    def get_default(field: str) -> Any:
        return models.Student._meta.get_field(field).default

    # Overwrite a number of target's student items if it is None or in the unknowns, while source isn't
    field_unknowns = {
        'birthdate': [],
        'ethnicity_id': [get_default('ethnicity')],
        'domicile_id': [get_default('domicile')],
        'nationality_id': [get_default('nationality')],
        'religion_or_belief_id': [get_default('religion_or_belief')],
        'gender': [],
        'sits_id': [],
        # Preserve any opt-ins
        'email_optin': [False],
        'email_optin_on': [],
        'email_optin_method': [''],
        'mail_optin': [False],
        'mail_optin_on': [],
        'mail_optin_method': [''],
    }

    for field, unknowns in field_unknowns.items():
        if getattr(target, field) in [None] + unknowns and getattr(source, field) not in [None] + unknowns:
            setattr(target, field, getattr(source, field))

    # Mergeable data - reassign source data that doesn't yet exist on the target to the target
    # todo: consider replicating redpot-legacy's existence checking, to avoid duplicates
    source.emails.update(student=target)
    source.phones.update(student=target)
    source.addresses.update(student=target)
    source.other_ids.update(student=target)
    source.website_accounts.update(student=target)

    # Set contact defaults to last modified if any exist
    # for table in (
    #     'address',
    #     'email',
    #     'phone',
    # ):
    #     newest_data = idb((idb[table].student == target.id)).select(orderby=~idb[table].modified_on).first()
    #     if newest_data:
    #         newest_data.update_record(is_default=True)

    # For logins, make most recently modified in combined set active
    target.website_accounts.update(is_disabled=True)
    newest_login = target.website_accounts.order_by('-modified_on').first()
    if newest_login:
        newest_login.is_disabled = False
        newest_login.save()

    # Child tables that follow a normal many-to-one structure (data never overlaps)
    # todo: move up?
    source.enquiries.update(student=target)
    source.suspensions.update(student=target)
    source.waitlists.update(student=target)

    Tutor.objects.filter(student=source).update(student=target)
    merge_one_to_ones(source=source, target=target)
    merge_qualification_aims(source=source, target=target)

    target.save()
    source.delete()


def merge_one_to_ones(*, source: models.Student, target: models.Student) -> None:
    for model in ('moodle_id', 'diet', 'emergency_contact'):
        source_child = getattr(source, model, None)
        if source_child:
            if hasattr(target, model):
                source_child.delete()
            else:
                source_child.student = target
                source_child.save()


def merge_qualification_aims(*, source: models.Student, target: models.Student) -> None:
    for qa in source.qualification_aims.all():
        # Check for a matching qualification aim on the target, and check that the source isn't award bearing
        matching_qa = target.qualification_aims.filter(programme_id=qa.programme_id).first()
        if matching_qa and not qa.programme.qualification.is_award:
            # Move enrolments
            qa.enrolments.update(qa=matching_qa.id)
            qa.delete()
        else:
            # Move entire QA
            qa.student = target
            qa.save()


def create_merge_archive_record(*, source: models.Student, target: models.Student) -> None:
    ...
    # Create a JSON archive of the student and child data
    # archive = (
    #     idb(idb.student.id == source.id)
    #     .select(
    #         idb.student.ALL,
    #         idb.address.ALL,
    #         idb.email.ALL,
    #         idb.phone.ALL,
    #         idb.qa.ALL,
    #         idb.enrolment.ALL,
    #         idb.login.ALL,
    #         idb.other_id.ALL,
    #         idb.diet.ALL,
    #         idb.moodle_id.ALL,
    #         left=[
    #             idb.address.on(idb.address.student == idb.student.id),
    #             idb.email.on(idb.email.student == idb.student.id),
    #             idb.phone.on(idb.phone.student == idb.student.id),
    #             idb.qa.on(idb.qa.student == idb.student.id),
    #             idb.enrolment.on(idb.enrolment.qa == idb.qa.id),
    #             idb.login.on(idb.login.student == idb.student.id),
    #             idb.other_id.on(idb.other_id.student == idb.student.id),
    #             idb.diet.on(idb.diet.student == idb.student.id),
    #             idb.moodle_id.on(idb.moodle_id.student == idb.student.id),
    #         ],
    #     )
    #     .as_json()
    # )

    # todo: create json via model_to_dict or django.core.serializers.serialize, attaching children manually

    # idb.student_archive.insert(source=source.id, target=target.id, husid=source.husid, json=archive)
