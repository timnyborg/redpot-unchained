import secrets
import string
from datetime import datetime
from io import BytesIO
from itertools import count
from typing import Iterator

import xlsxwriter

from django.db.models import Max, QuerySet

from apps.module.models import Module
from apps.student.models import Student

from . import models


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


def assign_moodle_id(*, student: Student, created_by: str, first_module_code: str) -> None:
    id_generator = next_moodle_id()
    models.MoodleID.objects.create(
        student=student,
        moodle_id=next(id_generator),
        first_module_code=first_module_code,
        created_by=created_by,
        modified_by=created_by,
    )


def assign_moodle_ids(*, module: Module, created_by: str):
    """
    Acquires and attaches MoodleIDs for students enrolled on a module.
    Marks newly generated IDs with the module code, so the
    report used by TALL can show new passwords and "same as before"
    """

    students = Student.objects.filter(
        qa__enrolment__module=module,
        qa__enrolment__status__takes_place=True,
    ).exclude(moodle_id__id__isnull=False)

    for student in students:
        assign_moodle_id(student=student, first_module_code=module.code, created_by=created_by)

    return len(students)


def get_random_string(*, length: int = 12):
    """Generate a random string from uppercase, lowercase, and digits
    https://docs.python.org/3/library/secrets.html#recipes-and-best-practices
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))


def generate_student_spreadsheet(*, module: Module, students: QuerySet[Student]) -> bytes:
    """Produces an excel file with the template information for adding students to an award-bearing moodle site"""
    output = BytesIO()
    with xlsxwriter.Workbook(output, {'in_memory': True}) as workbook:
        worksheet = workbook.add_worksheet()

        heading = workbook.add_format({'bold': True, 'font_size': 12})
        warning = workbook.add_format({'font_color': '#FF0000'})
        table_header = workbook.add_format({'bold': True, 'bottom': 1})

        row = count()

        worksheet.set_column(0, 12, 15)  # Widen the columns
        worksheet.write_row(next(row), 0, ['Moodle user request spreadsheet.'], cell_format=heading)
        worksheet.write_row(
            next(row),
            0,
            [
                'Fill in/correct the user information below (e.g. add staff details). '
                f'Then email to tallithelp@conted.ox.ac.uk. Please include "{module.title} ({module.code})" '
                'in the email subject line.'
            ],
            cell_format=warning,
        )
        worksheet.write_row(
            next(row),
            0,
            ['Students', 'Students for {module.title} ({module.code}). Retrieved on {module.start_date}'],
            cell_format=heading,
        )
        worksheet.write_row(
            next(row),
            0,
            [
                'username',
                'reminder',
                'password',
                'firstname',
                'lastname',
                'email',
                'city',
                'country',
                'role1',
                'auth',
                'maildisplay',
                'autosubscribe',
                'profile_field_courseids',
            ],
            cell_format=table_header,
        )

        for student in students:
            address = student.get_default_address()
            email = student.get_default_email()
            sso = student.get_sso()
            worksheet.write_row(
                next(row),
                1,
                [
                    f'{sso.number}@ox.ac.uk' if sso else '',
                    get_random_string(),
                    student.firstname,
                    student.surname,
                    email.email if email else '',
                    address.town if address else '',
                    address.country if address else '',
                    'student',
                    '',
                    0,
                    0,
                    module.code,
                ],
            )

        next(row) * 3

        worksheet.write_row(
            next(row), 0, ['Staff', 'You must fill in the details of the course staff here.'], cell_format=heading
        )
        worksheet.write_row(
            next(row),
            0,
            [
                'username',
                'reminder',
                'password',
                'firstname',
                'lastname',
                'email',
                'city',
                'country',
                'role1',
                'auth',
                'maildisplay',
                'autosubscribe',
                'profile_field_courseids',
            ],
            cell_format=table_header,
        )
        worksheet.write_row(next(row), 8, ['courseadmin', '', '0', '0', module.code])
        worksheet.write_row(next(row), 8, ['coursedirector', '', '0', '0', module.code])
        worksheet.write_row(next(row), 8, ['tutor', '', '0', '0', module.code])
        worksheet.write_row(next(row), 8, ['directorofstudies', '', '0', '0', module.code])
        worksheet.write_row(next(row), 8, ['observer', '', '0', '0', module.code])
        worksheet.write_row(next(row), 8, ['courseeditor', '', '0', '0', module.code])

        next(row)

        worksheet.write_row(
            next(row),
            0,
            [
                'Additions',
                'If you want to add users after you have already sent TALL a version of this file list them in this '
                'section, then re-send it to tallithelp@conted.ox.ac.uk. Only append changes - do not remove '
                'information already sent to TALL.',
            ],
            cell_format=heading,
        )
        worksheet.write_row(
            next(row),
            0,
            [
                'username',
                'reminder',
                'password',
                'firstname',
                'lastname',
                'email',
                'city',
                'country',
                'role1',
                'auth',
                'maildisplay',
                'autosubscribe',
                'profile_field_courseids',
            ],
            cell_format=table_header,
        )

        next(row) * 3

        worksheet.write_row(
            next(row),
            0,
            [
                'Removals',
                'If you want to remove users after you have already sent TALL a version of this file list them in this'
                ' section, then re-send it to tallithelp@conted.ox.ac.uk. Only append changes - do not remove '
                'information already sent to TALL.',
            ],
            cell_format=heading,
        )
        worksheet.write_row(next(row), 0, ['username', 'firstname', 'lastname', 'email'], cell_format=table_header)

        next(row) * 3

        worksheet.write_row(next(row), 0, ['Notes'], cell_format=heading)
        worksheet.write_row(
            next(row),
            0,
            [
                'username',
                'The user\'s Oxford username (sometimes called an SSO username), with "@ox.ac.uk" appended, i.e. in '
                'the form "abcd1234@ox.ac.uk". Required if available.',
            ],
        )
        worksheet.write_row(next(row), 0, ['reminder', 'For TALL\'s use.'])
        worksheet.write_row(
            next(row), 0, ['password', 'Administration field; do not add or change the password values.']
        )
        worksheet.write_row(next(row), 0, ['firstname', 'The user\'s first or preferred name. Required.'])
        worksheet.write_row(next(row), 0, ['lastname', 'The user\'s last name. Required.'])
        worksheet.write_row(next(row), 0, ['email', 'The user\'s email address. Required.'])
        worksheet.write_row(next(row), 0, ['city', 'The user\'s city of residence. Optional.'])
        worksheet.write_row(next(row), 0, ['country', 'The user\'s country of residence. Optional.'])
        worksheet.write_row(
            next(row), 0, ['role1', 'Choose from: "student", "tutor", "coursedirector", and "registry".']
        )
        worksheet.write_row(
            next(row),
            0,
            [
                'auth',
                'The students authentication method. If the user has an Oxford username, this should be "shibboleth".',
            ],
        )
        worksheet.write_row(next(row), 0, ['maildisplay', 'An email preference for the user. Always use "0" (zero).'])
        worksheet.write_row(
            next(row), 0, ['autosubscribe', 'An email preference for the user. Always use "0" (zero).']
        )
        worksheet.write_row(next(row), 0, ['profile_field_courseids', 'The course id. Required.'])

        next(row)

        worksheet.write_row(
            next(row),
            0,
            [
                'NB: This spreadsheet is not magic. Please email it to tallithelp@conted.ox.ac.uk in order to get your'
                ' user request fulfilled.'
            ],
        )

    return output.getvalue()
