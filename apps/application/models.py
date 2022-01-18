from django.db import models

from apps.core.models import SignatureModel


class Application(SignatureModel):
    module = models.ForeignKey(
        'module.Module',
        models.DO_NOTHING,
        db_column='module',
        related_name='course_applications',
        related_query_name='application',
    )
    student = models.ForeignKey(
        'student.Student',
        models.DO_NOTHING,
        db_column='student',
        null=True,
        related_name='course_applications',
        related_query_name='application',
    )

    academic_credit = models.BooleanField()
    # todo: rely on module to derive is_non_accredited
    is_non_accredited = models.BooleanField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)

    # todo: integrate personal data into student table (separate migration project), then remove columns
    title = models.CharField(max_length=20, blank=True, null=True)
    surname = models.CharField(max_length=40, blank=True, null=True)
    firstname = models.CharField(max_length=40, blank=True, null=True, db_column='fname')
    preferred_name = models.CharField(max_length=40, blank=True, null=True, db_column='pname')
    birthdate = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    nationality = models.ForeignKey('student.Nationality', models.DO_NOTHING, db_column='nationality', null=True)
    domicile = models.ForeignKey('student.Domicile', models.DO_NOTHING, db_column='residence', null=True)
    ethnicity = models.ForeignKey('student.Ethnicity', models.DO_NOTHING, db_column='ethnicity', null=True)
    religion = models.ForeignKey('student.Religion', models.DO_NOTHING, db_column='religion', null=True)
    disability = models.ForeignKey(
        'student.Disability', models.DO_NOTHING, db_column='disability', null=True, blank=True
    )
    disability_details = models.CharField(max_length=500, blank=True, null=True)
    email_optin = models.BooleanField(blank=True, null=True)
    post_optin = models.BooleanField(blank=True, null=True)
    dars_optin = models.BooleanField(blank=True, null=True)

    # todo: integrate address data into address table (separate migration project), then remove most columns
    address1 = models.CharField(max_length=128, blank=True, null=True)
    address2 = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    county_state = models.CharField(max_length=64, blank=True, null=True)
    # oddly, country stores a domicile id
    country = models.CharField(max_length=64, blank=True, null=True)
    postcode = models.CharField(max_length=32, blank=True, null=True)
    billing_address1 = models.CharField(max_length=128, blank=True, null=True)
    billing_address2 = models.CharField(max_length=128, blank=True, null=True)
    billing_city = models.CharField(max_length=64, blank=True, null=True)
    billing_county_state = models.CharField(max_length=64, blank=True, null=True)
    billing_postcode = models.CharField(max_length=32, blank=True, null=True)
    billing_country = models.CharField(max_length=64, blank=True, null=True)
    entry_qualification = models.ForeignKey(
        'qualification_aim.EntryQualification',
        models.DO_NOTHING,
        db_column='entry_qualification',
        null=True,
        blank=True,
    )
    entry_qualification_details = models.CharField(max_length=500, blank=True, null=True)
    occupation = models.CharField(max_length=128, blank=True, null=True)
    employer = models.CharField(max_length=128, blank=True, null=True)
    statement = models.CharField(max_length=4000, blank=True, null=True)
    funding = models.CharField(max_length=250, blank=True, null=True)
    invoice_details = models.CharField(max_length=200, blank=True, null=True)
    provenance = models.CharField(max_length=32, blank=True, null=True)
    provenance_details = models.CharField(max_length=128, blank=True, null=True)

    # todo: integrate email and phone into the relevant tables (separate migration project), then remove
    email = models.CharField(max_length=64, blank=True, null=True)
    phone = models.CharField(max_length=64, blank=True, null=True)

    # language - todo: consider separate table
    native_speaker = models.BooleanField(blank=True, null=True, db_column='native')
    test_type = models.CharField(max_length=64, blank=True, null=True)
    date_taken = models.DateField(blank=True, null=True)
    overall_result = models.CharField(max_length=128, blank=True, null=True)
    constituent_scores = models.CharField(max_length=128, blank=True, null=True)
    further_information = models.CharField(max_length=500, blank=True, null=True)

    # referee - todo: consider separate table
    referee_name = models.CharField(max_length=50, blank=True, null=True)
    referee_institution = models.CharField(max_length=128, blank=True, null=True)
    referee_email_address = models.CharField(max_length=64, blank=True, null=True)

    # invoicing/payment details
    company_name = models.CharField(max_length=128, blank=True, null=True)
    purchase_order = models.TextField(blank=True, null=True)
    invoice_or_quote = models.BooleanField(blank=True, null=True)
    further_details = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        db_table = 'course_application'


class Attachment(models.Model):
    application = models.ForeignKey(
        Application, models.CASCADE, related_name='attachments', related_query_name='attachment'
    )
    # todo: rename db columns
    title = models.CharField(max_length=50, blank=True, null=True, db_column='filename')
    filename = models.CharField(max_length=255, blank=True, null=True, db_column='attachment')

    class Meta:
        db_table = 'course_application_attachment'

    @property
    def full_url(self) -> str:
        # todo: implement, probably based on a setting, maybe a storage class
        return '#'
