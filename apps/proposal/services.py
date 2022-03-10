from django.db import transaction
from django.template.loader import render_to_string

from apps.module import services as module_services
from apps.module.models import Equipment, Subject
from apps.proposal.models import Proposal
from apps.tutor.models import Tutor

CLONE_FIELDS = [
    'title',
    'is_repeat',
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

    proposal.save()


@transaction.atomic
def update_module(*, proposal: Proposal) -> None:
    """Copy the data from a complete proposal to its source module"""

    module = proposal.module
    module.url = None  # rebuild from proposal title

    # fields with a straight copy
    for field in CLONE_FIELDS:
        setattr(module, field, getattr(proposal, field))

    module_services.build_recommended_reading(module=module)

    # Module subjects (clear all for a module then add the updated choices)
    module.subjects.set(Subject.objects.filter(pk__in=proposal.subjects))

    # Make sure the default equipment is also set (for CABS)
    module.equipment.set(Equipment.objects.filter(always_required=True))

    # Add all the updated choices
    for equipment in Equipment.objects.filter(pk__in=proposal.equipment):
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

    module.save()
