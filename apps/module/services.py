from __future__ import annotations

from datetime import datetime
from typing import Any

from django.contrib.auth.models import User
from django.template.loader import render_to_string

from .models import Book, Module

WEB_FIELDS = [
    # Text fields used for website copy.  Used in both clone_fields and copy_web_fields
    'overview',
    'snippet',
    'notification',
    'programme_details',
    'selection_criteria',
    'course_aims',
    'certification',
    'assessment_methods',
    'it_requirements',
    'level_and_demands',
    'recommended_reading',
    'teaching_methods',
    'teaching_outcomes',
    'accommodation',
    'payment',
    'scholarships',
    'how_to_apply',
    'further_details',
]


def copy_fees(*, source: Module, target: Module, user: User) -> int:
    """Copies all fees from one module to another"""
    fees = source.fees.all()
    for fee in fees:
        # Copy all attributes of a fee, excepting its ID, module and timestamp
        fee.pk = None  # See https://docs.djangoproject.com/en/3.0/topics/db/queries/#copying-model-instances
        fee.module = target
        fee.created_by = user.username
        fee.modified_by = user.username
        fee.created_on = datetime.now()
        fee.modified_on = datetime.now()
        fee.save()
    return len(fees)


def copy_books(*, source: Module, target: Module) -> None:
    for book in source.books.all():
        Book.objects.create(
            module=target,
            title=book.title,
            author=book.author,
            type=book.type,
            additional_information=book.additional_information,
            solo_link=book.solo_link,
            isbn_shelfmark=book.isbn_shelfmark,
        )


def clone_fields(*, source: Module, target: Module, copy_url: bool = False, copy_dates: bool = False) -> None:
    """Copy a module, optionally copying fees, programme attachments, persistent id, etc...
    You must call .save() yourself
    """

    field_list = [
        # General stuff.
        'credit_points',
        'max_size',
        'non_credit_bearing',
        'no_meetings',
        'meeting_time',
        'auto_publish',
        'email',
        'phone',
        'enrol_online',
        'auto_feedback',
        'auto_reminder',
        'image',
        'apply_url',
        'mailing_list',
        # Foreign keys.  Rely on _id for to avoid DB calls to get related objects
        'division_id',
        'format_id',
        'location_id',
        'points_level_id',
        'portfolio_id',
        'status_id',
        'terms_and_conditions',  # todo: convert to _id aftertable implemented
    ] + WEB_FIELDS

    if copy_url:
        field_list.append('url')
    if copy_dates:
        field_list += [
            'start_date',
            'end_date',
            'open_date',
            'closed_date',
            'publish_date',
            'unpublish_date',
            'start_time',
            'end_time',
        ]

    # Copy the fields one by one
    for field in field_list:
        setattr(target, field, getattr(source, field))


def copy_web_fields(*, source: Module, target: Module, user: User) -> None:
    """
    Copy only the website marketing fields from one module to another
    You must call .save() yourself
    """
    for field in WEB_FIELDS:
        setattr(target, field, getattr(source, field))
    target.modified_by = user.username
    target.modified_on = datetime.now()


def copy_children(*, source: Module, target: Module, user: User) -> None:
    """Copy all of a module's child records (subjects, programmes, marketing_types, tutors)"""
    timestamp = datetime.now()  # identical timing
    signature_fields: dict[str, Any] = {
        'created_by': user.username,
        'modified_by': user.username,
        'created_on': timestamp,
        'modified_on': timestamp,
    }

    target.subjects.add(*source.subjects.all())
    target.programmes.add(*source.programmes.all())
    target.marketing_types.add(*source.marketing_types.all())

    for tutor in source.tutor_modules.all():
        target.tutors.add(
            tutor.tutor,
            through_defaults={
                'role': tutor.role,
                'biography': tutor.biography,
                'is_published': tutor.is_published,
                'is_teaching': tutor.is_teaching,
                **signature_fields,
            },
        )

    for record in source.module_hecos_subjects.all():
        target.module_hecos_subjects.create(
            hecos_subject=record.hecos_subject,
            percentage=record.percentage,
            **signature_fields,
        )


def build_recommended_reading(*, module: Module) -> None:
    """Updates a module's recommended reading field with a template populated by the module's books
    You must call .save() yourself
    """
    reading_list = module.books.filter(type=Book.Types.PREPARATORY).order_by('author', 'title')
    module.recommended_reading = render_to_string(
        'module/components/recommended_reading_template.html',
        context={'module': module, 'reading_list': reading_list},
    )
