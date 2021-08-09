from django.db import models

from apps.core.models import SignatureModel


class CourseApplication(SignatureModel):
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

    academic_credit = models.BooleanField(blank=True, null=True)
    title = models.CharField(max_length=20, blank=True, null=True)
    surname = models.CharField(max_length=40, blank=True, null=True)
    first_name = models.CharField(max_length=40, blank=True, null=True, db_column='fname')
    previous_name = models.CharField(max_length=40, blank=True, null=True, db_column='pname')
    birthdate = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    nationality = models.SmallIntegerField(blank=True, null=True)
    residence = models.IntegerField(blank=True, null=True)
    address1 = models.CharField(max_length=128, blank=True, null=True)
    address2 = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    county_state = models.CharField(max_length=64, blank=True, null=True)
    postcode = models.CharField(max_length=32, blank=True, null=True)
    native = models.BooleanField(blank=True, null=True)
    entry_qualification = models.CharField(max_length=50, blank=True, null=True)
    entry_qualification_details = models.CharField(max_length=500, blank=True, null=True)
    occupation = models.CharField(max_length=128, blank=True, null=True)
    employer = models.CharField(max_length=128, blank=True, null=True)
    statement = models.CharField(max_length=4000, blank=True, null=True)
    funding = models.CharField(max_length=250, blank=True, null=True)
    invoice_details = models.CharField(max_length=200, blank=True, null=True)
    ethnicity = models.SmallIntegerField(blank=True, null=True)
    religion = models.SmallIntegerField(blank=True, null=True)
    disability = models.SmallIntegerField(blank=True, null=True)
    disability_details = models.CharField(max_length=500, blank=True, null=True)
    provenance = models.CharField(max_length=32, blank=True, null=True)
    provenance_details = models.CharField(max_length=128, blank=True, null=True)
    email_optin = models.BooleanField(blank=True, null=True)
    post_optin = models.BooleanField(blank=True, null=True)
    dars_optin = models.BooleanField(blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    email = models.CharField(max_length=64, blank=True, null=True)
    phone = models.CharField(max_length=64, blank=True, null=True)
    test_type = models.CharField(max_length=64, blank=True, null=True)
    date_taken = models.DateField(blank=True, null=True)
    overall_result = models.CharField(max_length=128, blank=True, null=True)
    constituent_scores = models.CharField(max_length=128, blank=True, null=True)
    further_information = models.CharField(max_length=500, blank=True, null=True)
    referee_name = models.CharField(max_length=50, blank=True, null=True)
    referee_institution = models.CharField(max_length=128, blank=True, null=True)
    referee_email_address = models.CharField(max_length=64, blank=True, null=True)
    attachment_name_1 = models.CharField(max_length=50, blank=True, null=True)
    is_completed = models.BooleanField(blank=True, null=True)
    hash = models.CharField(max_length=64, blank=True, null=True)
    is_billing_same_as_postal = models.BooleanField(blank=True, null=True)
    billing_address1 = models.CharField(max_length=128, blank=True, null=True)
    billing_address2 = models.CharField(max_length=128, blank=True, null=True)
    billing_city = models.CharField(max_length=64, blank=True, null=True)
    billing_county_state = models.CharField(max_length=64, blank=True, null=True)
    billing_postcode = models.CharField(max_length=32, blank=True, null=True)
    billing_country = models.CharField(max_length=64, blank=True, null=True)
    is_non_accredited = models.BooleanField(blank=True, null=True)
    company_name = models.CharField(max_length=128, blank=True, null=True)
    purchase_order = models.TextField(blank=True, null=True)
    invoice_or_quote = models.BooleanField(blank=True, null=True)
    further_details = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        db_table = 'course_application'
