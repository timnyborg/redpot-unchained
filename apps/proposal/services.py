from apps.proposal.models import Proposal


def populate_from_redpot(*, proposal: Proposal, language_course: bool = False) -> None:
    module = proposal.module

    # Module subjects
    module_subjects = module.subjects.all()
    proposal_subjects = list(sub.pk for sub in module_subjects)

    # Module equipment
    module_equipment = module.equipment.all()  # Remove duplicates
    proposal_equipment = list({item.pk for item in module_equipment})  # set to deduplicate

    # Programme details / grammar points skeleton
    weekly_template = f'<p>Courses starts: {module.start_date:%d %b %Y}</p>' + ''.join(
        f'<p>Week {week + 1}: &nbsp;</p>' for week in range(module.no_meetings or 10)
    )

    course_aims_template = '<p><b>Course Aim:<b/><br />&nbsp;</p><p><b>Course Objectives:</b><br />&nbsp;</p>'

    # todo: move these to template rendering

    if language_course:
        recommended_reading_template = f"""<p>All weekly class students may become borrowing members of the Rewley House Continuing Education Library for the duration of their course.
            Prospective students whose courses have not yet started are welcome to use the Library for reference. More information can be found on the&nbsp;<a href="http://www.bodleian.ox.ac.uk/conted">Library website.</a></p>
            <p>There is a&nbsp;<a href="http://ox.libguides.com/conted-weeklyclass">Guide for Weekly Class students</a> which will give you further information.&nbsp;</p>
            <p>Availability of titles on the reading list (below) can be checked on&nbsp;<a href="http://solo.bodleian.ox.ac.uk/">SOLO</a>, the library catalogue.</p>
            <p><a href="/courses/reading-list/{module.id}">Recommended Reading List</a></p>"""
    else:
        recommended_reading_template = f"""<p>All weekly class students may become borrowing members of the Rewley House Continuing Education Library for the duration of their course.
            Prospective students whose courses have not yet started are welcome to use the Library for reference. More information can be found on the&nbsp;<a href="http://www.bodleian.ox.ac.uk/conted">Library website.</a></p>
            <p>There is a&nbsp;<a href="http://ox.libguides.com/conted-weeklyclass">Guide for Weekly Class students</a> which will give you further information.&nbsp;</p>
            <p>You will need to buy the coursebook which will be required throughout the course.
            Books labelled as optional (below) may be available from the library and can be checked on&nbsp;<a href="http://solo.bodleian.ox.ac.uk/">SOLO</a>, the library catalogue.</p>
            <p><a href="/courses/reading-list/{module.id}">Recommended Reading List</a></p>"""

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
    proposal.programme_details = module.programme_details or weekly_template
    proposal.course_aims = module.course_aims or course_aims_template
    proposal.equipment = proposal_equipment
    proposal.subjects = proposal_subjects
    proposal.image = module.image
    proposal.recommended_reading = module.recommended_reading or recommended_reading_template
    proposal.grammar_points = weekly_template if proposal.limited else None

    proposal.save()
