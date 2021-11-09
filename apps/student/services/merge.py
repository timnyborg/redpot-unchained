from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.tutor.models import Tutor

from .. import models
from .archive_serializers import StudentSerializer


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


def student_to_archive_dict(student: models.Student) -> dict:
    return StudentSerializer(student).data

    # idb.student_archive.insert(source=source.id, target=target.id, husid=source.husid, json=archive)
