"""A collection of methods to output standard text sections for print publicity"""

from django.db.models import Min

from apps.fee.models import FeeTypes
from apps.module.models import Module
from apps.tutor.models import Tutor

WEEKLY_PORTFOLIO = 32


def strip_online(title: str) -> str:
    """Removes (Online) from course titles"""
    return title.replace('(Online)', '').replace('(online)', '').strip()


def get_marketing_types(module: Module) -> list:
    # aggregation in python, because this is prefetched elsewhere
    return [item.id for item in module.marketing_types.all()]


def render_tutors(module: Module) -> str:
    tutors = Tutor.objects.filter(
        modules=module, tutor_module__is_teaching=True, tutor_module__is_published=True
    ).select_related('student')

    formatted = []
    for tutor in tutors:
        # Unify title and use nickname when one exists
        prefix = tutor_prefix(tutor.student.title or '', tutor.qualifications or '')
        nick_or_first = tutor.student.nickname or tutor.student.firstname
        formatted.append(f'{prefix} {nick_or_first} {tutor.student.surname}')
    return ', '.join(formatted)


def render_format(module) -> str:
    result = ''
    marketing_types = get_marketing_types(module)
    if 3 in marketing_types:
        result = 'Professional; '
    if 6 in marketing_types:
        result += 'Hybrid teaching'
    elif module.format_id == 4:
        result += 'Summer school'
    elif module.format_id == 3:
        result += 'Online - flexible'
    elif module.format_id == 6:
        result += 'Online - live'
    else:
        result += 'In-person'
    return result


def render_credit(module: Module) -> str:
    if not module.credit_points:
        return ''
    text = f'Credit: {module.credit_points} CATS points'
    if module.points_level:
        text += f' (FHEQ-{module.points_level.fheq_level})'
    return text


def render_min_fee(module: Module) -> str:
    # todo: make this an annotation on the shared base query?
    min_fee = module.fees.filter(type=FeeTypes.PROGRAMME, amount__gt=0, is_visible=True).aggregate(
        min_fee=Min('amount')
    )['min_fee']
    if min_fee:
        return f'From £{min_fee:.0f}'
    return 'Unknown fees'


def tutor_prefix(title: str, qualifications: str) -> str:
    """Attach 'Prof' by title or 'Dr' if one of the qualifications are Phd or DPhil"""
    qualifications = qualifications.replace('.', '').lower()
    if title[:4].lower() == 'prof':
        return 'Prof'
    elif 'dphil' in qualifications or 'phd' in qualifications:
        return 'Dr'
    return ''


def render_times(module: Module) -> str:
    times = ''
    # Display weekday before time on weekly
    if module.portfolio == WEEKLY_PORTFOLIO and module.start_date:
        times = f'{module.start_date.strftime("%A")}s '

    start, end = module.start_time, module.end_time
    if start and end:
        # Only show minutes if not a round hour
        if start.minute != 0:
            start_format = '%-I.%M'
        else:
            start_format = '%-I'

        # Show AM/PM for both, otherwise it'll only show after end time
        if start.hour < 12 <= end.hour:
            start_format += '%p'

        if end.minute != 0:
            end_format = '%-I.%M%p'
        else:
            end_format = '%-I%p'

        times += f'{start.strftime(start_format)}-{end.strftime(end_format)}'.lower()
    return times.strip()


def render_dates(module: Module) -> str:
    """Return dates in format 'Monday 3 Jan 2019 to 7 Jan 2020'"""
    date_format = '%-d %b %Y'
    date_format_no_year = '%-d %b'
    start, end = module.start_date, module.end_date
    if not start or not end:
        return 'Dates TBC'
    if start == end:
        formatted_start = start.strftime(date_format)
        return f'{formatted_start}'
    if start.year == end.year:
        formatted_start = start.strftime(date_format_no_year)
    else:
        formatted_start = start.strftime(date_format)
    formatted_end = end.strftime(date_format)
    return f'From {formatted_start} to {formatted_end}'


def render_location(module: Module) -> str:
    location = module.location
    if not location:
        return ''
    elif location.city == 'Oxford':
        return location.building
    elif location.city:
        return location.city
    return ''


def render_meetings_and_location(module: Module) -> str:
    meetings_and_location = ''
    if module.no_meetings and module.no_meetings > 1:
        meetings_word = 'weeks' if module.format_id == 3 else 'meetings'
        meetings_and_location = f'{module.no_meetings} {meetings_word}'
    if module.format_id == 1:
        meetings_and_location += ', ' + render_location(module)
    return meetings_and_location.strip(', ')
