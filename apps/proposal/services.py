from django.conf import settings
from django.core import mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.core.utils import dates
from apps.module import services as module_services
from apps.module.models import Equipment, Subject
from apps.tutor.models import Tutor

from .models import Proposal

CLONE_FIELDS = [
    'title',
    'location',
    'address',
    'room',
    'start_date',
    'michaelmas_end',
    'hilary_start',
    'end_date',
    'start_time',
    'end_time',
    'no_meetings',
    'max_size',
    'snippet',
    'overview',
    'level_and_demands',
    'assessment_methods',
    'teaching_methods',
    'teaching_outcomes',
    'programme_details',
    'course_aims',
    'image',
]


def populate_from_module(*, proposal: Proposal) -> None:
    """Clone fields from a module to its proposal, with some default html for web fields"""
    module = proposal.module

    # fields with a straight copy
    for field in CLONE_FIELDS:
        setattr(proposal, field, getattr(module, field))

    # fields with conditional copying
    weekly_template = render_to_string(
        "proposal/components/programme_details.html",
        context={'module': module, 'weeks': range(1, (module.no_meetings or 10) + 1)},
    )
    course_aims_template = render_to_string("proposal/components/course_aims.html")
    template = 'proposal/components/' + (
        'recommended_reading_languages.html' if proposal.limited else 'recommended_reading.html'
    )
    recommended_reading = render_to_string(template, context={'module': module})

    proposal.programme_details = proposal.programme_details or weekly_template
    proposal.course_aims = proposal.course_aims or course_aims_template
    proposal.recommended_reading = module.recommended_reading or recommended_reading

    module_equipment = module.equipment.all()
    proposal_equipment = list({item.pk for item in module_equipment})  # set to deduplicate
    proposal.equipment = proposal_equipment

    module_subjects = module.subjects.all()
    proposal_subjects = [sub.pk for sub in module_subjects]
    proposal.subjects = proposal_subjects

    proposal.grammar_points = weekly_template if proposal.limited else None

    # Fill tutor fields to allow them to suggest changes
    proposal.tutor_title = proposal.tutor.student.title
    proposal.tutor_nickname = proposal.tutor.student.nickname
    proposal.tutor_biography = (
        proposal.tutor_on_module_record
        and proposal.tutor_on_module_record.biography  # Module-level bio
        or proposal.tutor.biography  # or tutor's standard bio
    )

    proposal.save()


@transaction.atomic
def update_module(*, proposal: Proposal) -> None:
    """Copy the data from a complete proposal to its source module and tutor"""

    module = proposal.module
    module.url = None  # rebuild from proposal title

    # fields with a straight copy
    for field in CLONE_FIELDS:
        setattr(module, field, getattr(proposal, field))

    module_services.build_recommended_reading(module=module)

    # Module subjects (clear all for a module then add the updated choices)
    module.subjects.set(Subject.objects.filter(pk__in=proposal.subjects or []))

    # Make sure the default equipment is also set (for CABS)
    module.equipment.set(Equipment.objects.filter(always_required=True))

    # Add all the updated choices
    for equipment in Equipment.objects.filter(pk__in=proposal.equipment or []):
        module.equipment.add(
            equipment,
            # Add note for scientific equipment items  # todo: reconsider pk-based logic
            through_defaults={'note': proposal.scientific_equipment if equipment.pk == 13 else ''},
        )

    # If DoS has a tutor record, add it to the module
    dos_record = Tutor.objects.filter(
        student__firstname=proposal.dos.first_name,
        student__surname=proposal.dos.last_name,
        student__email__email=proposal.dos.email,
    ).first()

    if dos_record:
        record, created = module.tutor_modules.get_or_create(
            tutor=dos_record,
            defaults={
                'role': 'Director of studies',
                'director_of_studies': True,
                'is_teaching': False,
            },
        )
        if not created:
            record.director_of_studies = True
            record.save()

    # Update tutor-related fields
    proposal.tutor.student.title = proposal.tutor_title
    proposal.tutor.student.nickname = proposal.tutor_nickname
    proposal.tutor.student.save()

    tutor_on_module = proposal.tutor_on_module_record
    if tutor_on_module:
        tutor_on_module.biography = proposal.tutor_biography
        tutor_on_module.save()

    module.save()


SUBJECT_STEM = 'Weekly Classes and Weekly Oxford Worldwide course proposal request '
APP_URL = settings.PUBLIC_APPS_URL + '/course-proposal'


def email_tutor_prompt(*, proposal: Proposal, reminder: bool = False) -> None:
    """Sends the proposal's tutor an email directing them to the online form.
    If a reminder, it includes any messages from the DoS
    """
    recipient_list = [settings.SUPPORT_EMAIL] if settings.DEBUG else [proposal.tutor.student.get_default_email()]
    subject_suffix = '- reminder' if reminder else ''
    messages = proposal.messages.all() if reminder else []
    proposal.tutor.populate_hash_id()  # todo: can be removed if all tutors have hash_ids
    link_hash = proposal.tutor.hash_id
    body = render_to_string(
        'proposal/email/tutor_prompt.html',
        context={
            'proposal': proposal,
            'link_hash': link_hash,
            'messages': messages,
            'app_url': APP_URL,
            'academic_year': dates.academic_year(proposal.start_date),
        },
    )
    mail.send_mail(
        from_email=proposal.module.email,
        recipient_list=recipient_list,
        subject=SUBJECT_STEM + subject_suffix,
        message=strip_tags(body),
        html_message=body,
    )


def email_tutor_submission_confirmation(*, proposal: Proposal) -> None:
    """Sends the proposal's tutor an email confirming submission"""
    recipient_list = [settings.SUPPORT_EMAIL] if settings.DEBUG else [proposal.tutor.student.get_default_email()]
    subject_suffix = 'submitted and sent for approval'
    body = render_to_string('proposal/email/tutor_submit.html', context={'proposal': proposal})
    mail.send_mail(
        from_email=proposal.module.email,
        recipient_list=recipient_list,
        subject=SUBJECT_STEM + subject_suffix,
        message=strip_tags(body),
        html_message=body,
    )


def email_dos_prompt(*, proposal: Proposal, reminder: bool = False) -> None:
    """Sends the proposal's director of studies an email (after tutor submission) directing them to the online form."""
    recipient_list = [settings.SUPPORT_EMAIL] if settings.DEBUG else [proposal.dos.email]
    subject_suffix = f'from {proposal.tutor.student} requires your attention'
    if reminder:
        subject_suffix += ' - reminder'

    link_hash = proposal.dos.hash_id
    body = render_to_string(
        'proposal/email/dos_prompt.html',
        context={'proposal': proposal, 'link_hash': link_hash, 'app_url': APP_URL},
    )
    mail.send_mail(
        from_email=proposal.module.email,
        recipient_list=recipient_list,
        subject=SUBJECT_STEM + subject_suffix,
        message=strip_tags(body),
        html_message=body,
    )


def email_admin_submission_confirmation(*, proposal: Proposal) -> None:
    """Sends admin an email notifying them of tutor submission"""
    recipient_list = [settings.SUPPORT_EMAIL] if settings.DEBUG else [proposal.module.email]
    subject_suffix = f'sent to director of studies {proposal.dos.get_full_name()} for review'
    body = render_to_string(
        'proposal/email/admin_tutor_submitted.html',
        context={'proposal': proposal, 'redpot_url': settings.CANONICAL_URL},
    )
    mail.send_mail(
        from_email=proposal.module.email,
        recipient_list=recipient_list,
        subject=SUBJECT_STEM + subject_suffix,
        message=strip_tags(body),
        html_message=body,
    )


def email_admin_prompt(*, proposal: Proposal) -> None:
    """Sends admin an email notifying them of director of studies approval, and linking them to redpot"""
    recipient_list = [settings.SUPPORT_EMAIL] if settings.DEBUG else [proposal.module.email]
    subject_suffix = 'awaits your final review and approval'
    body = render_to_string(
        'proposal/email/admin_prompt.html', context={'proposal': proposal, 'redpot_url': settings.CANONICAL_URL}
    )
    mail.send_mail(
        from_email=proposal.module.email,
        recipient_list=recipient_list,
        subject=SUBJECT_STEM + subject_suffix,
        message=strip_tags(body),
        html_message=body,
    )


def email_tutor_on_completion(*, proposal: Proposal) -> None:
    """Sends a proposal's tutor an email notifying them that their proposal has been approved and finalized"""
    recipient_list = [settings.SUPPORT_EMAIL] if settings.DEBUG else [proposal.tutor.student.get_default_email()]
    subject_suffix = 'completed successfully'
    body = render_to_string('proposal/email/tutor_complete.html', context={'proposal': proposal})
    # todo: determine whether we need to attach/include the summary file: body.append(_summary_file(proposal.id))
    mail.send_mail(
        from_email=proposal.module.email,
        recipient_list=recipient_list,
        subject=SUBJECT_STEM + subject_suffix,
        message=strip_tags(body),
        html_message=body,
    )
