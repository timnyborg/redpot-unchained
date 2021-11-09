from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.tutor.models import Tutor

from .. import models
from . import archive_serializers


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
def merge_students(*, source: models.Student, target: models.Student) -> None:
    """Merge the source student record into the target record"""
    if hasattr(source, 'tutor') and hasattr(target, 'tutor'):
        raise CannotMergeError("Both records are tutors.  This can't be handled yet.")
    if source.sits_id and target.sits_id and source.sits_id != target.sits_id:
        raise CannotMergeError('Conflicting SITS IDs')

    _create_merge_archive_record(source=source, target=target)

    _merge_properties(source=source, target=target)
    _merge_children(source=source, target=target)
    _merge_one_to_ones(source=source, target=target)
    _merge_qualification_aims(source=source, target=target)

    target.save()
    source.delete()


def _merge_properties(*, source: models.Student, target: models.Student) -> None:
    """Overwrite the target's student properties if they are None or unknown"""

    def get_default(field: str) -> Any:
        return models.Student._meta.get_field(field).default

    field_unknown_values = {
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
    for field, unknowns in field_unknown_values.items():
        if getattr(target, field) in [None] + unknowns and getattr(source, field) not in [None] + unknowns:
            setattr(target, field, getattr(source, field))


def _merge_children(*, source: models.Student, target: models.Student) -> None:
    """Reassign the source's child record (reverse foreign keys) to the target"""
    # todo: consider replicating redpot-legacy's existence checking, to avoid duplicates
    source.emails.update(student=target)
    source.phones.update(student=target)
    source.addresses.update(student=target)
    source.other_ids.update(student=target)
    source.website_accounts.update(student=target)
    source.enquiries.update(student=target)
    source.suspensions.update(student=target)
    source.waitlists.update(student=target)

    # For contacts, make most recently modified the default
    for model in ('addresses', 'emails', 'phones'):
        children = getattr(target, model)
        children.update(is_default=False)
        latest_record = children.order_by('-modified_on').first()
        if latest_record:
            latest_record.is_default = True
            latest_record.save()

    # For logins, make most recently modified active
    target.website_accounts.update(is_disabled=True)
    newest_login = target.website_accounts.order_by('-modified_on').first()
    if newest_login:
        newest_login.is_disabled = False
        newest_login.save()


def _merge_one_to_ones(*, source: models.Student, target: models.Student) -> None:
    Tutor.objects.filter(student=source).update(student=target)
    for model in ('moodle_id', 'diet', 'emergency_contact'):
        source_child = getattr(source, model, None)
        if source_child:
            if hasattr(target, model):
                source_child.delete()
            else:
                source_child.student = target
                source_child.save()


def _merge_qualification_aims(*, source: models.Student, target: models.Student) -> None:
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


def _create_merge_archive_record(*, source: models.Student, target: models.Student) -> models.StudentArchive:
    """Serializes the source student and creates an archive record"""
    archive_data = archive_serializers.StudentSerializer(source).data
    return models.StudentArchive.objects.create(source=source.id, target=target.id, json=archive_data)
