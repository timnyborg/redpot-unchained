from django.template.loader import render_to_string

from apps.proposal.models import Proposal


def populate_from_module(*, proposal: Proposal) -> None:
    """Clone fields from a module to its proposal, with some default html for web fields"""
    module = proposal.module

    clone_fields = [
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
    ]
    # fields with a straight copy
    for field in clone_fields:
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

    proposal.programme_details = module.programme_details or weekly_template
    proposal.course_aims = module.course_aims or course_aims_template
    proposal.recommended_reading = module.recommended_reading or recommended_reading

    module_equipment = module.equipment.all()
    proposal_equipment = list({item.pk for item in module_equipment})  # set to deduplicate
    proposal.equipment = proposal_equipment

    module_subjects = module.subjects.all()
    proposal_subjects = [sub.pk for sub in module_subjects]
    proposal.subjects = proposal_subjects

    proposal.image = module.image
    proposal.grammar_points = weekly_template if proposal.limited else None

    proposal.save()
