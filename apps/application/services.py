from datetime import datetime

from django.db import transaction

import apps.enrolment.services as enrolment_services
from apps.core.models import User
from apps.enrolment.models import Enrolment, EnrolmentStatus, Statuses
from apps.qualification_aim.models import QualificationAim
from apps.student.models import (
    NOT_KNOWN_DOMICILE,
    NOT_KNOWN_ETHNICITY,
    NOT_KNOWN_NATIONALITY,
    Address,
    Domicile,
    Email,
    Phone,
    Student,
)


@transaction.atomic
def create_student_from_application(*, application, user: User) -> Student:
    """Generates a student record, plus phone, email, and address records, from an application
    Will be rendered obsolete by reworking application form to use core tables
    """

    timestamp_fields = {'created_by': user.username, 'modified_by': user.username}

    # For non accredited course application forms and non credit bearing course application forms
    student = Student.objects.create(
        title=application.title,
        firstname=application.firstname,
        surname=application.surname,
        nickname=application.preferred_name,
        birthdate=application.birthdate,
        gender=application.gender,
        disability=application.disability,
        disability_detail=application.disability_details,
        # todo: complex _id assignments can be sorted if required for all applications
        ethnicity_id=application.ethnicity.id if application.ethnicity else NOT_KNOWN_ETHNICITY,
        nationality_id=application.nationality.id if application.nationality else NOT_KNOWN_NATIONALITY,
        domicile_id=application.domicile.id if application.domicile else NOT_KNOWN_DOMICILE,
        highest_qualification=application.entry_qualification,
        occupation=application.occupation,
        religion_or_belief=application.religion,
        dars_optout=not application.dars_optin,
        **timestamp_fields,
    )
    # Update marketing preferences
    if application.email_optin:
        student.email_optin = True
        student.email_optin_on = datetime.now()
        student.email_optin_method = 'Registration form'
    if application.post_optin:
        student.mail_optin = True
        student.mail_optin_on = datetime.now()
        student.mail_optin_method = 'Registration form'
    student.save()

    # Contact records
    if application.email:
        Email.objects.create(student=student, email=application.email, **timestamp_fields)
    if application.phone:
        Phone.objects.create(student=student, number=application.phone, is_default=True, **timestamp_fields)

    # Standard address
    Address.objects.create(
        line1=application.address1.strip(),
        line2=(application.address2 or '').strip(),
        town=(application.city or '').strip(),
        countystate=(application.county_state or '').strip(),
        country=Domicile.objects.get(pk=application.country).name,
        postcode=(application.postcode or '').strip(),
        is_default=True,
        student=student,
        **timestamp_fields,
    )
    if application.billing_address1:
        # Set company name on a new line if it exists
        line_1 = application.billing_address1.strip()
        line_2 = (application.billing_address2 or '').strip()
        line_3 = ''
        if application.company_name:
            line_1, line_2, line_3 = application.company_name.strip(), line_1, line_2

        # Add a billing address
        Address.objects.create(
            line1=line_1,
            line2=line_2,
            line3=line_3,
            town=(application.billing_city or '').strip(),
            countystate=(application.billing_county_state or '').strip(),
            country=Domicile.objects.get(pk=application.billing_country).name,
            postcode=(application.billing_postcode or '').strip(),
            is_billing=True,
            student=student,
            **timestamp_fields,
        )
    return student


@transaction.atomic
def enrol_applicant(*, application, user) -> Enrolment:
    """Provisionally enrol an applicant on the application module, creating a qualification_aim if required"""
    if not application.student:
        raise ValueError('Application has no student record attached')
    # Get the module's non-award programme (assume there is only 1)
    programme = application.module.programmes.filter(qualification__is_award=False).first()
    qualification_aim, _ = QualificationAim.objects.get_or_create(
        student=application.student,
        programme=programme,
        defaults={'created_by': user.username, 'modified_by': user.username},
    )
    return enrolment_services.create_enrolment(
        qa=qualification_aim,
        module=application.module,
        status=EnrolmentStatus.objects.get(pk=Statuses.PROVISIONAL),
        user=user,
    )
