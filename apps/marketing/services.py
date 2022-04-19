from __future__ import annotations

from datetime import date, datetime, time
from itertools import groupby
from operator import itemgetter
from typing import Generator, Tuple

from lxml import etree

from django.db.models import Q
from django.utils.text import slugify

from apps.module.models import Module, Subject

from . import utils

DATES_TBD_STATUSES = (23, 24)

BASE_QUERY = (
    Module.objects.filter(is_cancelled=False, no_search=False)
    .select_related('points_level', 'portfolio', 'location')
    .prefetch_related('marketing_types')
    .defer(None)
    .distinct()
)
PUBLISHED_TBD = Q(start_date__isnull=True, status__in=DATES_TBD_STATUSES, is_published=True)


WEEKLY_PORTFOLIO = 32
DAY_WEEKEND_PORTFOLIO = 31
ONLINE_PORTFOLIO = 17


def prospectus(*, start_from: datetime) -> Generator:
    """One file per subject, with modules in chronological order, with lots of detail"""
    subjects = Subject.objects.order_by('area').values_list('area', flat=True).distinct()
    for subject in subjects:
        root = etree.Element('document')
        modules = BASE_QUERY.filter(
            Q(start_date__gte=start_from) | PUBLISHED_TBD,
            subjects__area=subject,
        ).exclude(snippet='')

        # Languages have their own sort order
        if 'language' in subject:
            modules = modules.order_by('title')
        else:
            modules = modules.order_by('start_date', 'start_time')

        for module in modules:
            item = etree.SubElement(root, 'item')
            etree.SubElement(item, 'title').text = utils.strip_online(module.title)

            # Lowest price listed
            fee_text = utils.render_min_fee(module)
            etree.SubElement(item, 'price-and-code').text = f'{fee_text} {module.code}'

            # Meta consists of several sections of semicolon-separated text
            meta_sections = [
                utils.render_format(module),
                utils.render_dates(module),
                utils.render_times(module),
                utils.render_meetings_and_location(module),
                utils.render_credit(module),
            ]
            etree.SubElement(item, 'meta').text = '; '.join(filter(None, meta_sections))  # Strip out empty strings

            # Snippet only once for each title
            snippet = etree.SubElement(item, 'snippet')
            snippet.text = module.snippet

            # if marketing type includes 4 (lecture series) add tag
            if 4 in utils.get_marketing_types(module):
                etree.SubElement(snippet, 'lecture_series').text = 'Lecture series'

        # Blank heading for award
        etree.SubElement(root, 'item').text = 'Award courses'
        yield f'{subject}.xml', root


def subject_area_brochures(*, start_from: datetime) -> Generator:
    """One file per subject, with modules in chronological order, with format info in the title element's name"""
    subjects = Subject.objects.order_by('area').values_list('area', flat=True).distinct()
    subsections = [
        (1, 'Weekly classes in Oxford', 'O%'),
        (1, 'Weekly classes outside Oxford', 'E%'),
        (2, 'Day and weekend events', None),
        (3, 'Flexible online courses', None),
        (6, 'Live online courses', None),
        (4, 'Summer schools', None),
        (5, 'Professional development', None),
    ]
    for subject in subjects:
        root = etree.Element('document')
        for format_id, description, code_mask in subsections:
            el_title = 'title-' + slugify(description)
            modules = BASE_QUERY.filter(
                Q(start_date__gte=start_from) | PUBLISHED_TBD,
                subjects__area=subject,
                format=format_id,
            ).exclude(snippet='')

            if code_mask:  # Allows us to filter out Reading courses easyish
                modules = modules.filter(code__like=code_mask)

            modules = modules.order_by('start_date', 'start_time', 'url')

            for module in modules:
                marketing_types = utils.get_marketing_types(module)
                item = etree.SubElement(root, 'item')
                etree.SubElement(item, el_title).text = utils.strip_online(module.title)

                if format_id == 1:
                    # Tutors only for weekly
                    etree.SubElement(item, 'tutor').text = utils.render_tutors(module)

                # Meta consists of several sections of semicolon-separated text
                meta_sections = [
                    utils.render_times(module),
                    utils.render_dates(module),
                ]
                etree.SubElement(item, 'meta').text = '; '.join(filter(None, meta_sections))  # Strip out empty strings

                snippet = etree.SubElement(item, 'snippet')
                snippet.text = module.snippet

                # if marketing type includes 4 (lecture series) add tag
                if 4 in marketing_types:
                    etree.SubElement(snippet, 'lecture_series').text = 'Lecture series'
        yield f'{subject}.xml', root


def newspaper(*, start_from: datetime) -> Generator:
    """One file per portfolio, ordered by subject (with subject headers) and date"""
    subjects = Subject.objects.order_by('area').values_list('area', flat=True).distinct()
    subsections = [
        (WEEKLY_PORTFOLIO, 'Weekly classes in Oxford', 'O%'),
        (DAY_WEEKEND_PORTFOLIO, 'Day and weekend events', None),
        (ONLINE_PORTFOLIO, 'Online courses', None),
    ]
    for portfolio, description, code_mask in subsections:
        root = etree.Element('document')
        el_title = 'title-' + slugify(description)
        for subject in subjects:
            modules = (
                BASE_QUERY.filter(
                    Q(start_date__gte=start_from) | PUBLISHED_TBD,
                    subjects__area=subject,
                    portfolio=portfolio,
                )
                .exclude(snippet='')
                .order_by('url', 'start_date', 'start_time')
            )

            if code_mask:  # Allows us to filter out courses outside oxford
                modules = modules.filter(code__like=code_mask)

            # Subject heading at the start of each section
            if modules:
                etree.SubElement(root, 'subject').text = subject

            # Grouping lets us treat multiple runs as one
            groups = groupby(modules, lambda r: r.url)

            # Attach the earliest start dates to each group (for sorting)
            sortable_groups = []
            for key, modules in groups:
                module_list = list(modules)  # allow using the groupby generator twice
                earliest_start = min(
                    (module.start_date or date(2999, 1, 1), module.start_time or time(23, 59))
                    for module in module_list
                )
                sortable_groups.append((key, module_list, earliest_start))

            # Sort by start_date if not 'language'
            if 'language' in subject.lower():
                sortable_groups.sort(key=itemgetter(0))  # Url/title
            else:
                sortable_groups.sort(key=itemgetter(2))  # Min(start_date, start_time)

            for _, modules, _ in sortable_groups:
                item = etree.SubElement(root, 'item')
                for index, module in enumerate(list(modules)):
                    is_first_run = index == 0
                    if is_first_run:
                        etree.SubElement(item, el_title).text = utils.strip_online(module.title)

                        if portfolio == WEEKLY_PORTFOLIO:
                            # Tutors only for weekly
                            etree.SubElement(item, 'tutor').text = utils.render_tutors(module)

                    # Lowest price listed
                    fee_text = utils.render_min_fee(module)
                    etree.SubElement(item, 'price-and-code').text = f'{fee_text} {module.code}'

                    meta_sections = []

                    if portfolio != ONLINE_PORTFOLIO:
                        # Non-online-flexible courses show format
                        meta_sections.append(utils.render_format(module))

                    meta_sections += [
                        utils.render_times(module),
                        utils.render_dates(module),
                        utils.render_meetings_and_location(module),
                        utils.render_credit(module),
                    ]
                    meta = etree.SubElement(item, 'meta')
                    meta.text = '; '.join(filter(None, meta_sections))

                    # if marketing type includes 4 (lecture series) add tag
                    if 4 in utils.get_marketing_types(module):
                        etree.SubElement(meta, 'lecture_series').text = 'Lecture series'

        yield f'{description}.xml', root
