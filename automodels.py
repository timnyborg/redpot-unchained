# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Accommodation(models.Model):
    enrolment = models.ForeignKey('Enrolment', models.DO_NOTHING, db_column='enrolment')
    type = models.IntegerField(blank=True, null=True)
    note = models.CharField(max_length=256, blank=True, null=True)
    created_by = models.CharField(max_length=64, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=64, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    limit = models.ForeignKey('Limit', models.DO_NOTHING, db_column='limit', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'accommodation'


class AcornPostcodes(models.Model):
    postcode = models.CharField(max_length=16)
    no_spaces = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = 'acorn_postcodes'


class Activity(models.Model):
    description = models.CharField(max_length=128, blank=True, null=True)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'activity'


class Address(models.Model):
    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student')
    type = models.ForeignKey('AddressType', models.DO_NOTHING, db_column='type', blank=True, null=True)
    line1 = models.CharField(max_length=128, blank=True, null=True)
    line2 = models.CharField(max_length=128, blank=True, null=True)
    line3 = models.CharField(max_length=128, blank=True, null=True)
    town = models.CharField(max_length=64, blank=True, null=True)
    countystate = models.CharField(max_length=64, blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    postcode = models.CharField(max_length=32, blank=True, null=True)
    formatted = models.CharField(max_length=1024, blank=True, null=True)
    is_default = models.BooleanField()
    is_billing = models.BooleanField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    sits_type = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'address'


class AddressType(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'address_type'


class Amendment(models.Model):
    type = models.ForeignKey('AmendmentType', models.DO_NOTHING, db_column='type')
    status = models.ForeignKey('AmendmentStatus', models.DO_NOTHING, db_column='status')
    enrolment = models.IntegerField()
    requested_on = models.DateTimeField()
    requested_by = models.TextField()
    approved_on = models.DateTimeField(blank=True, null=True)
    approved_by = models.TextField(blank=True, null=True)
    executed_on = models.DateTimeField(blank=True, null=True)
    executed_by = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    approver = models.CharField(max_length=16, blank=True, null=True)
    transfer_module = models.TextField(blank=True, null=True)
    transfer_enrolment = models.IntegerField(blank=True, null=True)
    invoice = models.IntegerField(blank=True, null=True)
    source_invoice = models.IntegerField(blank=True, null=True)
    transfer_invoice = models.IntegerField(blank=True, null=True)
    reason = models.ForeignKey('AmendmentReason', models.DO_NOTHING, db_column='reason', blank=True, null=True)
    batch = models.IntegerField(blank=True, null=True)
    narrative = models.CharField(max_length=128, blank=True, null=True)
    is_complete = models.BooleanField()
    actioned_online = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'amendment'


class AmendmentReason(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.IntegerField()
    reason = models.TextField()

    class Meta:
        managed = False
        db_table = 'amendment_reason'


class AmendmentStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    status = models.TextField()
    icon = models.TextField()

    class Meta:
        managed = False
        db_table = 'amendment_status'


class AmendmentType(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.TextField()
    action = models.TextField()
    supported = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'amendment_type'


class AuthCas(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    service = models.CharField(max_length=512, blank=True, null=True)
    ticket = models.CharField(max_length=512, blank=True, null=True)
    renew = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_cas'


class AuthEvent(models.Model):
    time_stamp = models.DateTimeField(blank=True, null=True)
    client_ip = models.CharField(max_length=512, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    origin = models.CharField(max_length=512, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_event'


class AuthGroup(models.Model):
    role = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthMembership(models.Model):
    id = models.AutoField()
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_membership'
        unique_together = (('user', 'group'),)


class AuthPermission(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=512, blank=True, null=True)
    table_name = models.CharField(max_length=512, blank=True, null=True)
    record_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_permission'


class AuthUser(models.Model):
    first_name = models.CharField(max_length=128, blank=True, null=True)
    last_name = models.CharField(max_length=128, blank=True, null=True)
    full_name = models.CharField(max_length=256, blank=True, null=True)
    username = models.CharField(unique=True, max_length=16, blank=True, null=True)
    password = models.CharField(max_length=16)
    registration_id = models.CharField(max_length=512, blank=True, null=True)
    division = models.ForeignKey('Division', models.DO_NOTHING, db_column='division', blank=True, null=True)
    email = models.CharField(max_length=512, blank=True, null=True)
    reset_password_key = models.CharField(max_length=512, blank=True, null=True)
    registration_key = models.CharField(max_length=512, blank=True, null=True)
    date_format = models.IntegerField(blank=True, null=True)
    default_approver = models.CharField(max_length=32, blank=True, null=True)
    role = models.CharField(max_length=512, blank=True, null=True)
    image = models.CharField(max_length=512, blank=True, null=True)
    phone = models.CharField(max_length=512, blank=True, null=True)
    room = models.CharField(max_length=512, blank=True, null=True)
    is_active = models.BooleanField()
    on_facewall = models.BooleanField()
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_user'


class AutoNumber(models.Model):
    id = models.AutoField()
    name = models.CharField(max_length=32)
    next_no = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auto_number'
        unique_together = (('id', 'name', 'next_no'),)


class Banner(models.Model):
    message = models.TextField()
    type = models.IntegerField()
    publish = models.DateField(blank=True, null=True)
    unpublish = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'banner'


class Book(models.Model):
    module = models.ForeignKey('Module', models.DO_NOTHING, db_column='module')
    title = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=24)
    additional_information = models.TextField(blank=True, null=True)
    solo_link = models.TextField(blank=True, null=True)
    isbn_shelfmark = models.TextField(db_column='ISBN_shelfmark', blank=True, null=True)  # Field name made lowercase.
    price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    library_note = models.TextField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'book'


class BookStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    status = models.TextField()

    class Meta:
        managed = False
        db_table = 'book_status'


class Catering(models.Model):
    id = models.AutoField()
    fee = models.ForeignKey('Fee', models.DO_NOTHING, db_column='fee', blank=True, null=True)
    enrolment = models.ForeignKey('Enrolment', models.DO_NOTHING, db_column='enrolment', blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'catering'


class CertheMarks(models.Model):
    qa = models.ForeignKey('Qa', models.DO_NOTHING, db_column='qa')
    courses_transferred_in = models.TextField(blank=True, null=True)
    credits_transferred_in = models.IntegerField(blank=True, null=True)
    subject = models.CharField(max_length=8, blank=True, null=True)
    assignment1_date = models.DateField(blank=True, null=True)
    assignment1_grade = models.IntegerField(blank=True, null=True)
    assignment2_date = models.DateField(blank=True, null=True)
    assignment2_grade = models.IntegerField(blank=True, null=True)
    assignment3_date = models.DateField(blank=True, null=True)
    assignment3_grade = models.IntegerField(blank=True, null=True)
    journal1_date = models.DateField(blank=True, null=True)
    journal2_date = models.DateField(blank=True, null=True)
    journal_cats_points = models.IntegerField(blank=True, null=True)
    is_introductory_course = models.BooleanField(blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=64, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'certhe_marks'


class CourseApplication(models.Model):
    academic_credit = models.BooleanField(blank=True, null=True)
    title = models.CharField(max_length=20, blank=True, null=True)
    surname = models.CharField(max_length=40, blank=True, null=True)
    fname = models.CharField(max_length=40, blank=True, null=True)
    pname = models.CharField(max_length=40, blank=True, null=True)
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
    module = models.ForeignKey('Module', models.DO_NOTHING, db_column='module', blank=True, null=True)
    is_completed = models.BooleanField(blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=50, blank=True, null=True)
    student = models.IntegerField(blank=True, null=True)
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
        managed = False
        db_table = 'course_application'


class CourseApplicationAttachment(models.Model):
    application_id = models.IntegerField(blank=True, null=True)
    filename = models.CharField(max_length=50, blank=True, null=True)
    attachment = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'course_application_attachment'


class DateFormats(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=32)
    format = models.CharField(max_length=16)
    sample = models.CharField(max_length=16)
    jsformat = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = 'date_formats'


class Diet(models.Model):
    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student')
    type = models.ForeignKey('DietType', models.DO_NOTHING, db_column='type', blank=True, null=True)
    note = models.CharField(max_length=512, blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'diet'
        unique_together = (('student', 'type'),)


class DietType(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'diet_type'


class Disability(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64, blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    web_publish = models.BooleanField()
    display_order = models.IntegerField(blank=True, null=True)
    custom_description = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'disability'
        unique_together = (('id', 'description', 'custom_description'),)


class Discount(models.Model):
    name = models.TextField()
    code = models.CharField(max_length=20)
    percent = models.IntegerField(blank=True, null=True)
    usable_once = models.BooleanField(blank=True, null=True)
    expires_on = models.DateField(blank=True, null=True)
    module_mask = models.CharField(max_length=20, blank=True, null=True)
    portfolio = models.ForeignKey('Portfolio', models.DO_NOTHING, db_column='portfolio', blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'discount'
        unique_together = (('code', 'usable_once'),)


class DiscountStudent(models.Model):
    id = models.AutoField()
    discount = models.ForeignKey(Discount, models.DO_NOTHING, db_column='discount')
    student = models.IntegerField()
    redeemed = models.BooleanField(blank=True, null=True)
    expires_on = models.DateField(blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'discount_student'


class Division(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    shortname = models.CharField(max_length=8, blank=True, null=True)
    email = models.CharField(max_length=256, blank=True, null=True)
    finance_prefix = models.CharField(max_length=2, blank=True, null=True)
    manager = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='manager', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'division'


class Domicile(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    fullname = models.CharField(max_length=64, blank=True, null=True)
    is_in_eu = models.BooleanField(blank=True, null=True)
    hesa_code = models.CharField(max_length=8, blank=True, null=True)
    sort_order = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'domicile'


class Email(models.Model):
    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student')
    email = models.CharField(max_length=64, blank=True, null=True)
    note = models.CharField(max_length=128, blank=True, null=True)
    is_default = models.BooleanField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    mailchimp_web_id = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'email'


class EmergencyContact(models.Model):
    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student', blank=True, null=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    email = models.CharField(max_length=128, blank=True, null=True)
    created_by = models.CharField(max_length=32, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=32, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'emergency_contact'


class Enquiry(models.Model):
    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student', blank=True, null=True)
    module = models.ForeignKey('Module', models.DO_NOTHING, db_column='module', blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    detail = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'enquiry'


class Enrolment(models.Model):
    qa = models.ForeignKey('Qa', models.DO_NOTHING, db_column='qa', blank=True, null=True)
    module = models.ForeignKey('Module', models.DO_NOTHING, db_column='module', blank=True, null=True)
    status = models.ForeignKey('EnrolmentStatus', models.DO_NOTHING, db_column='status', blank=True, null=True)
    result = models.ForeignKey('EnrolmentResult', models.DO_NOTHING, db_column='result')
    points_awarded = models.IntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    provenance = models.IntegerField(blank=True, null=True)
    provenance_details = models.CharField(max_length=128, blank=True, null=True)
    no_image_consent = models.BooleanField(blank=True, null=True)
    mark = models.IntegerField(blank=True, null=True)
    transcript_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'enrolment'


class EnrolmentResult(models.Model):
    id = models.CharField(primary_key=True, max_length=4)
    description = models.CharField(max_length=128, blank=True, null=True)
    is_active = models.BooleanField()
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    display_order = models.IntegerField(blank=True, null=True)
    hesa_code = models.CharField(max_length=1, blank=True, null=True)
    allow_certificate = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'enrolment_result'


class EnrolmentStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64, blank=True, null=True)
    takes_place = models.BooleanField()
    is_debtor = models.BooleanField()
    on_hesa_return = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'enrolment_status'


class EntryQualification(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    description = models.CharField(max_length=128, blank=True, null=True)
    custom_description = models.CharField(max_length=128, blank=True, null=True)
    elq_rank = models.IntegerField(blank=True, null=True)
    web_publish = models.BooleanField(db_column='web_Publish', blank=True, null=True)  # Field name made lowercase.
    display_order = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'entry_qualification'


class Equipment(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    ewert_cabs_code = models.CharField(max_length=10, blank=True, null=True)
    rewley_cabs_code = models.CharField(max_length=10, blank=True, null=True)
    always_required = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'equipment'


class Ethnicity(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=32, blank=True, null=True)
    is_active = models.BooleanField()
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    custom_description = models.CharField(max_length=64, blank=True, null=True)
    display_order = models.IntegerField(blank=True, null=True)
    web_publish = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'ethnicity'


class Feedback(models.Model):
    module = models.ForeignKey('Module', models.DO_NOTHING, db_column='module')
    rate_tutor = models.IntegerField(blank=True, null=True)
    rate_content = models.IntegerField(blank=True, null=True)
    rate_admin = models.IntegerField(blank=True, null=True)
    rate_facilities = models.IntegerField(blank=True, null=True)
    rate_refreshments = models.IntegerField(blank=True, null=True)
    rate_accommodation = models.IntegerField(blank=True, null=True)
    your_name = models.TextField(blank=True, null=True)
    hash_id = models.CharField(max_length=40, blank=True, null=True)
    notified = models.DateTimeField(blank=True, null=True)
    submitted = models.DateTimeField(blank=True, null=True)
    avg_score = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    reminder = models.DateTimeField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'feedback'


class FeedbackAdmin(models.Model):
    module = models.ForeignKey('Module', models.DO_NOTHING, db_column='module')
    updated = models.DateTimeField(blank=True, null=True)
    admin_comments = models.TextField(blank=True, null=True)
    person = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'feedback_admin'


class HecosSubject(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    definition = models.CharField(max_length=255, blank=True, null=True)
    cost_centre = models.ForeignKey('HesaCostCentre', models.DO_NOTHING, db_column='cost_centre', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hecos_subject'


class HesaCostCentre(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64, blank=True, null=True)
    price_group = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hesa_cost_centre'


class HesaSubject(models.Model):
    jacs_code = models.CharField(primary_key=True, max_length=8)
    description = models.CharField(max_length=64, blank=True, null=True)
    general_subject = models.CharField(max_length=64, blank=True, null=True)
    cost_centre = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hesa_subject'


class Invoice(models.Model):
    number = models.IntegerField()
    prefix = models.CharField(max_length=32, blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    fao = models.CharField(max_length=128, blank=True, null=True)
    invoiced_to = models.CharField(max_length=128, blank=True, null=True)
    line1 = models.CharField(max_length=128, blank=True, null=True)
    line2 = models.CharField(max_length=128, blank=True, null=True)
    line3 = models.CharField(max_length=128, blank=True, null=True)
    town = models.CharField(max_length=64, blank=True, null=True)
    countystate = models.CharField(max_length=64, blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    postcode = models.CharField(max_length=32, blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    custom_narrative = models.BooleanField()
    narrative = models.TextField(blank=True, null=True)
    ref_no = models.CharField(max_length=64, blank=True, null=True)
    division = models.IntegerField(blank=True, null=True)
    allocation = models.IntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    duedate = models.DateField(blank=True, null=True)
    contact_person = models.CharField(max_length=128, blank=True, null=True)
    contact_email = models.CharField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=64, blank=True, null=True)
    company = models.CharField(max_length=128, blank=True, null=True)
    formatted_addressee = models.TextField(blank=True, null=True)
    referred = models.BooleanField()
    vat_no = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'invoice'


class InvoiceLedger(models.Model):
    id = models.AutoField()
    ledger = models.ForeignKey('Ledger', models.DO_NOTHING, db_column='ledger')
    invoice = models.ForeignKey(Invoice, models.DO_NOTHING, db_column='invoice')
    allocation = models.IntegerField(blank=True, null=True)
    item_no = models.IntegerField(blank=True, null=True)
    type = models.ForeignKey('TransactionType', models.DO_NOTHING, db_column='type', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'invoice_ledger'


class Kmi(models.Model):
    id = models.AutoField()
    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student')
    subject_area = models.CharField(max_length=255, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=64, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kmi'


class Ledger(models.Model):
    date = models.DateTimeField(blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    finance_code = models.CharField(max_length=64, blank=True, null=True)
    narrative = models.CharField(max_length=128, blank=True, null=True)
    division = models.ForeignKey(Division, models.DO_NOTHING, db_column='division', blank=True, null=True)
    type = models.ForeignKey('TransactionType', models.DO_NOTHING, db_column='type', blank=True, null=True)
    account = models.ForeignKey('LedgerAccount', models.DO_NOTHING, db_column='account', blank=True, null=True)
    enrolment = models.ForeignKey(Enrolment, models.DO_NOTHING, db_column='enrolment', blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    allocation = models.IntegerField(blank=True, null=True)
    ref_no = models.IntegerField(blank=True, null=True)
    batch = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ledger'


class LedgerAccount(models.Model):
    id = models.AutoField()
    code = models.CharField(primary_key=True, max_length=64)
    description = models.CharField(max_length=64, blank=True, null=True)
    is_hidden = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'ledger_account'
        unique_together = (('code', 'is_hidden'),)


class Limit(models.Model):
    description = models.CharField(max_length=128, blank=True, null=True)
    places = models.IntegerField(blank=True, null=True)
    www_buffer = models.IntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'limit'


class Login(models.Model):
    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student')
    username = models.CharField(max_length=256)
    password = models.CharField(max_length=256, blank=True, null=True)
    is_disabled = models.BooleanField(blank=True, null=True)
    reset_password_key = models.CharField(max_length=512, blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'login'
        unique_together = (('student', 'username'),)


class MarketingType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'marketing_type'


class MenuHeadings(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    root_menu = models.CharField(max_length=50, blank=True, null=True)
    column_width = models.IntegerField(blank=True, null=True)
    heading_order = models.IntegerField(blank=True, null=True)
    column_number = models.IntegerField(blank=True, null=True)
    overview = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'menu_headings'


class MenuLinks(models.Model):
    menu_heading_id = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    url = models.CharField(max_length=256, blank=True, null=True)
    column_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'menu_links'


class MergeCandidates(models.Model):
    source = models.IntegerField()
    target = models.IntegerField()
    merged = models.BooleanField()
    created_by = models.CharField(max_length=64, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=64, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'merge_candidates'


class Module(models.Model):
    code = models.CharField(max_length=12)
    type = models.ForeignKey('ModuleType', models.DO_NOTHING, db_column='type', blank=True, null=True)
    persistent_id = models.CharField(max_length=64, blank=True, null=True)
    title = models.CharField(max_length=80)
    hesa_subject1 = models.ForeignKey(HesaSubject, models.DO_NOTHING, db_column='hesa_subject1', blank=True, null=True)
    hesa_subject1_percent = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    hesa_subject2 = models.CharField(max_length=8, blank=True, null=True)
    hesa_subject2_percent = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    publish_date = models.DateField(blank=True, null=True)
    open_date = models.DateField(blank=True, null=True)
    closed_date = models.DateTimeField(blank=True, null=True)
    unpublish_date = models.DateField(blank=True, null=True)
    max_size = models.IntegerField(blank=True, null=True)
    single_places = models.IntegerField(blank=True, null=True)
    twin_places = models.IntegerField(blank=True, null=True)
    double_places = models.IntegerField(blank=True, null=True)
    location = models.ForeignKey(Location, models.DO_NOTHING, db_column='location', blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    meeting_time = models.CharField(max_length=32, blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)
    no_meetings = models.IntegerField(blank=True, null=True)
    division = models.IntegerField()
    portfolio = models.IntegerField()
    auto_publish = models.BooleanField()
    status = models.ForeignKey('ModuleStatus', models.DO_NOTHING, db_column='status')
    is_published = models.BooleanField()
    finance_code = models.CharField(max_length=64, blank=True, null=True)
    email = models.CharField(max_length=256, blank=True, null=True)
    phone = models.CharField(max_length=256, blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    source_module_code = models.CharField(max_length=12, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    accommodation = models.TextField(blank=True, null=True)
    application = models.TextField(blank=True, null=True)
    assessment_methods = models.TextField(blank=True, null=True)
    certification = models.TextField(blank=True, null=True)
    course_aims = models.TextField(blank=True, null=True)
    level_and_demands = models.TextField(blank=True, null=True)
    libraries = models.TextField(blank=True, null=True)
    payment = models.TextField(blank=True, null=True)
    programme_details = models.TextField(blank=True, null=True)
    recommended_reading = models.TextField(blank=True, null=True)
    scholarships = models.TextField(blank=True, null=True)
    snippet = models.CharField(max_length=512, blank=True, null=True)
    teaching_methods = models.TextField(blank=True, null=True)
    teaching_outcomes = models.TextField(blank=True, null=True)
    selection_criteria = models.TextField(blank=True, null=True)
    it_requirements = models.TextField(blank=True, null=True)
    full_time_equivalent = models.DecimalField(max_digits=4, decimal_places=1)
    credit_points = models.IntegerField(blank=True, null=True)
    points_level = models.IntegerField(blank=True, null=True)
    enrol_online = models.BooleanField(blank=True, null=True)
    non_credit_bearing = models.BooleanField()
    auto_feedback = models.BooleanField()
    auto_reminder = models.BooleanField()
    no_search = models.BooleanField()
    week_number = models.IntegerField(blank=True, null=True)
    url = models.CharField(max_length=256, blank=True, null=True)
    adhocfee = models.CharField(db_column='adhocFee', max_length=1012, blank=True, null=True)  # Field name made lowercase.
    custom_fee = models.CharField(max_length=1012, blank=True, null=True)
    format = models.ForeignKey('ModuleFormat', models.DO_NOTHING, db_column='format', blank=True, null=True)
    image = models.CharField(max_length=512, blank=True, null=True)
    is_cancelled = models.BooleanField()
    default_non_credit = models.BooleanField(blank=True, null=True)
    note = models.CharField(max_length=512, blank=True, null=True)
    terms_and_conditions = models.ForeignKey('TermsAndConditions', models.DO_NOTHING, db_column='terms_and_conditions')
    apply_url = models.CharField(max_length=512, blank=True, null=True)
    further_details = models.TextField(blank=True, null=True)
    is_repeat = models.BooleanField()
    reminder_sent_on = models.DateTimeField(blank=True, null=True)
    room = models.CharField(max_length=12, blank=True, null=True)
    room_setup = models.CharField(max_length=12, blank=True, null=True)
    hilary_start = models.DateField(blank=True, null=True)
    michaelmas_end = models.DateField(blank=True, null=True)
    mailing_list = models.CharField(max_length=25, blank=True, null=True)
    notification = models.CharField(max_length=512, blank=True, null=True)
    cost_centre = models.CharField(max_length=6, blank=True, null=True)
    activity_code = models.CharField(max_length=2, blank=True, null=True)
    source_of_funds = models.CharField(max_length=5, blank=True, null=True)
    fee_code = models.CharField(max_length=1, blank=True, null=True)
    term_starts = models.DateField(blank=True, null=True)
    half_term = models.DateField(blank=True, null=True)
    image_upload = models.CharField(max_length=512, blank=True, null=True)
    reading_list_url = models.TextField(blank=True, null=True)
    reading_list_links = models.BooleanField(blank=True, null=True)
    invoice_online = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module'


class ModuleCabsBooking(models.Model):
    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module')
    mbr_id = models.TextField(blank=True, null=True)
    confirmed = models.IntegerField(blank=True, null=True)
    provisional = models.IntegerField(blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_cabs_booking'


class ModuleEquipment(models.Model):
    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module')
    equipment = models.ForeignKey(Equipment, models.DO_NOTHING, db_column='equipment')
    note = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_equipment'


class ModuleHecosSubject(models.Model):
    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module')
    hecos_subject = models.ForeignKey(HecosSubject, models.DO_NOTHING, db_column='hecos_subject')
    percentage = models.IntegerField()
    created_by = models.CharField(max_length=50, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=50, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_hecos_subject'


class ModuleHesaSubject(models.Model):
    module = models.IntegerField()
    subject = models.CharField(max_length=8, blank=True, null=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_hesa_subject'


class ModuleMarketingType(models.Model):
    id = models.AutoField()
    marketing_type = models.ForeignKey(MarketingType, models.DO_NOTHING, db_column='marketing_type', blank=True, null=True)
    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_marketing_type'
        unique_together = (('module', 'marketing_type'),)


class ModulePaymentPlan(models.Model):
    id = models.AutoField()
    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module', blank=True, null=True)
    plan_type = models.IntegerField()
    deposit = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_payment_plan'


class ModuleRoom(models.Model):
    id = models.AutoField()
    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module')
    room = models.ForeignKey('Room', models.DO_NOTHING, db_column='room')
    setup = models.CharField(max_length=12)
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_room'


class ModuleStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64, blank=True, null=True)
    publish = models.BooleanField(blank=True, null=True)
    short_desc = models.CharField(max_length=50, blank=True, null=True)
    waiting_list = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_status'


class ModuleSubject(models.Model):
    id = models.AutoField()
    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module', blank=True, null=True)
    subject = models.ForeignKey('Subject', models.DO_NOTHING, db_column='subject')
    id_0 = models.AutoField(db_column='id')  # Field renamed because of name conflict.
    batch = models.IntegerField(blank=True, null=True)
    modid_fk = models.CharField(db_column='MODID_FK', max_length=32, blank=True, null=True)  # Field name made lowercase.
    costcn = models.IntegerField(db_column='COSTCN', blank=True, null=True)  # Field name made lowercase.
    modsbjp = models.IntegerField(db_column='MODSBJP', blank=True, null=True)  # Field name made lowercase.
    modsbj = models.CharField(db_column='MODSBJ', max_length=6, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'module_subject'


class ModuleType(models.Model):
    type = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'module_type'


class ModuleWaitlist(models.Model):
    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module')
    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student')
    listed_on = models.DateTimeField(blank=True, null=True)
    emailed_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_waitlist'


class MoodleId(models.Model):
    id = models.AutoField()
    moodle_id = models.IntegerField(blank=True, null=True)
    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student')
    first_module_code = models.CharField(max_length=12, blank=True, null=True)
    created_by = models.CharField(max_length=64, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=64, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'moodle_id'
        unique_together = (('moodle_id', 'student'),)


class Nationality(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    fullname = models.CharField(max_length=64, blank=True, null=True)
    is_in_eu = models.BooleanField(blank=True, null=True)
    hesa_code = models.CharField(max_length=8, blank=True, null=True)
    sort_order = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nationality'


class NextHusid(models.Model):
    year = models.IntegerField(blank=True, null=True)
    next = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'next_husid'


class OtherId(models.Model):
    id = models.AutoField()
    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student', blank=True, null=True)
    number = models.CharField(max_length=64, blank=True, null=True)
    type = models.ForeignKey('OtherIdType', models.DO_NOTHING, db_column='type', blank=True, null=True)
    note = models.CharField(max_length=64, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'other_id'


class OtherIdType(models.Model):
    description = models.CharField(max_length=64, blank=True, null=True)
    msaccess_mask = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'other_id_type'


class OtherPayment(models.Model):
    student = models.IntegerField()
    payment_ref = models.CharField(max_length=16)
    title = models.TextField(blank=True, null=True)
    firstname = models.TextField(blank=True, null=True)
    surname = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    address3 = models.TextField(blank=True, null=True)
    town = models.TextField(blank=True, null=True)
    county = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    postcode = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    fee = models.IntegerField(blank=True, null=True)
    enrolment = models.IntegerField(blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=12, blank=True, null=True)
    complete = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'other_payment'


class Payment(models.Model):
    student = models.IntegerField()
    payment_ref = models.TextField()
    discount_code = models.TextField(blank=True, null=True)
    event = models.IntegerField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    firstname = models.TextField(blank=True, null=True)
    surname = models.TextField(blank=True, null=True)
    email = models.TextField()
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    address3 = models.TextField(blank=True, null=True)
    town = models.TextField(blank=True, null=True)
    county = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    postcode = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.TextField()
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.TextField(blank=True, null=True)
    voucher = models.IntegerField(blank=True, null=True)
    voucher_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment'


class PaymentItem(models.Model):
    payment = models.ForeignKey(Payment, models.DO_NOTHING, db_column='payment')
    student = models.IntegerField(blank=True, null=True)
    enrolment = models.IntegerField(blank=True, null=True)
    code = models.TextField(blank=True, null=True)
    firstname = models.TextField(blank=True, null=True)
    surname = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    hash_id = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    entry_qualification = models.ForeignKey(EntryQualification, models.DO_NOTHING, db_column='entry_qualification', blank=True, null=True)
    fees = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    domicile = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment_item'


class PaymentPlan(models.Model):
    type = models.ForeignKey('PaymentPlanType', models.DO_NOTHING, db_column='type', blank=True, null=True)
    status = models.ForeignKey('PaymentPlanStatus', models.DO_NOTHING, db_column='status', blank=True, null=True)
    invoice = models.IntegerField(blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    deposit = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment_plan'


class PaymentPlanSchedule(models.Model):
    id = models.AutoField()
    payment_plan = models.ForeignKey(PaymentPlan, models.DO_NOTHING, db_column='payment_plan', blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    is_deposit = models.BooleanField()
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment_plan_schedule'


class PaymentPlanStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment_plan_status'


class PaymentPlanType(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    deposit = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    payments = models.IntegerField(blank=True, null=True)
    payments_due = models.CharField(max_length=32, blank=True, null=True)
    start_month = models.IntegerField(blank=True, null=True)
    default_plan = models.IntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment_plan_type'


class PayrollUpload(models.Model):
    employee_no = models.CharField(max_length=32, blank=True, null=True)
    appointment_id = models.CharField(max_length=32, blank=True, null=True)
    nino = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payroll_upload'


class Phone(models.Model):
    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student')
    type = models.ForeignKey('PhoneType', models.DO_NOTHING, db_column='type')
    number = models.CharField(max_length=64, blank=True, null=True)
    note = models.CharField(max_length=128, blank=True, null=True)
    is_default = models.BooleanField()
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'phone'


class PhoneType(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'phone_type'


class PointsLevel(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    fheq_level = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'points_level'


class PolarPostcodes(models.Model):
    no_spaces = models.CharField(primary_key=True, max_length=10)
    quintile = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'polar_postcodes'


class Portfolio(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    division = models.ForeignKey(Division, models.DO_NOTHING, db_column='division', blank=True, null=True)
    email = models.CharField(max_length=256, blank=True, null=True)
    phone = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'portfolio'


class Post(models.Model):
    your_message = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'post'


class Programme(models.Model):
    persistent_id = models.CharField(max_length=64, blank=True, null=True)
    title = models.CharField(max_length=96, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    division = models.ForeignKey(Division, models.DO_NOTHING, db_column='division', blank=True, null=True)
    portfolio = models.IntegerField(blank=True, null=True)
    qualification = models.ForeignKey('Qualification', models.DO_NOTHING, db_column='qualification')
    created_by = models.CharField(max_length=8, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=8, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    student_load = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    funding_level = models.IntegerField(blank=True, null=True)
    funding_source = models.IntegerField(blank=True, null=True)
    study_mode = models.IntegerField(blank=True, null=True)
    study_location = models.SmallIntegerField(blank=True, null=True)
    reporting_year_type = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField()
    sits_code = models.CharField(max_length=32, blank=True, null=True)
    contact_list_display = models.BooleanField()
    short_name = models.CharField(max_length=64, blank=True, null=True)
    email = models.CharField(max_length=64, blank=True, null=True)
    phone = models.CharField(max_length=64, blank=True, null=True)
    mailing_list_id = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'programme'


class ProgrammeHecosSubject(models.Model):
    programme = models.ForeignKey(Programme, models.DO_NOTHING, db_column='programme')
    hecos_subject = models.ForeignKey(HecosSubject, models.DO_NOTHING, db_column='hecos_subject')
    percentage = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'programme_hecos_subject'


class ProgrammeHesaSubject(models.Model):
    programme = models.ForeignKey(Programme, models.DO_NOTHING, db_column='programme', blank=True, null=True)
    subject = models.ForeignKey(HesaSubject, models.DO_NOTHING, db_column='subject', blank=True, null=True)
    percentage = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'programme_hesa_subject'


class ProgrammeModule(models.Model):
    id = models.AutoField()
    programme = models.ForeignKey(Programme, models.DO_NOTHING, db_column='programme', blank=True, null=True)
    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'programme_module'
        unique_together = (('programme', 'module'), ('module', 'programme'),)


class ProgrammeStaff(models.Model):
    programme = models.ForeignKey(Programme, models.DO_NOTHING, db_column='programme')
    staff = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='staff')
    role = models.ForeignKey('StaffRole', models.DO_NOTHING, db_column='role')
    note = models.CharField(max_length=64, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=32, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'programme_staff'


class Proposal(models.Model):
    status = models.ForeignKey('ProposalStatus', models.DO_NOTHING, db_column='status')
    module = models.OneToOneField(Module, models.DO_NOTHING, db_column='module')
    title = models.CharField(max_length=80, blank=True, null=True)
    subjects = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    michaelmas_end = models.DateField(blank=True, null=True)
    hilary_start = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    half_term = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    no_meetings = models.IntegerField(blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)
    is_repeat = models.BooleanField(blank=True, null=True)
    previous_run = models.CharField(max_length=12, blank=True, null=True)
    location = models.CharField(max_length=32, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    room = models.CharField(max_length=12, blank=True, null=True)
    room_setup = models.CharField(max_length=12, blank=True, null=True)
    max_size = models.IntegerField(blank=True, null=True)
    reduced_size = models.IntegerField(blank=True, null=True)
    reduction_reason = models.CharField(max_length=50, blank=True, null=True)
    tutor = models.IntegerField()
    tutor_title = models.CharField(max_length=16, blank=True, null=True)
    tutor_firstname = models.CharField(max_length=40, blank=True, null=True)
    tutor_nickname = models.CharField(max_length=64, blank=True, null=True)
    tutor_surname = models.CharField(max_length=40, blank=True, null=True)
    tutor_qualifications = models.CharField(max_length=256, blank=True, null=True)
    tutor_biography = models.TextField(blank=True, null=True)
    field_trips = models.CharField(max_length=60, blank=True, null=True)
    risk_form = models.CharField(max_length=255, blank=True, null=True)
    snippet = models.TextField(blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    programme_details = models.TextField(blank=True, null=True)
    course_aims = models.TextField(blank=True, null=True)
    level_and_demands = models.TextField(blank=True, null=True)
    assessment_methods = models.TextField(blank=True, null=True)
    teaching_methods = models.TextField(blank=True, null=True)
    teaching_outcomes = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    equipment = models.TextField(blank=True, null=True)
    scientific_equipment = models.CharField(max_length=64, blank=True, null=True)
    additional_requirements = models.TextField(blank=True, null=True)
    recommended_reading = models.TextField(blank=True, null=True)
    dos = models.CharField(max_length=16, blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    allow_pd_edit = models.BooleanField(blank=True, null=True)
    grammar_points = models.TextField(blank=True, null=True)
    limited = models.BooleanField(blank=True, null=True)
    updated_fields = models.TextField(blank=True, null=True)
    tutor_approve = models.DateTimeField(blank=True, null=True)
    dos_approve = models.DateTimeField(blank=True, null=True)
    admin_approve = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    reminded_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'proposal'


class ProposalMessage(models.Model):
    proposal = models.IntegerField()
    sender = models.CharField(max_length=16)
    sent_on = models.DateTimeField()
    message = models.TextField()

    class Meta:
        managed = False
        db_table = 'proposal_message'


class ProposalNotation(models.Model):
    id = models.IntegerField(primary_key=True)
    column = models.CharField(max_length=40)
    notation = models.TextField()

    class Meta:
        managed = False
        db_table = 'proposal_notation'


class ProposalStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    status = models.TextField()
    icon = models.TextField()

    class Meta:
        managed = False
        db_table = 'proposal_status'


class PublicAuthCas(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    service = models.CharField(max_length=512, blank=True, null=True)
    ticket = models.CharField(max_length=512, blank=True, null=True)
    renew = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'public_auth_cas'


class PublicAuthEvent(models.Model):
    time_stamp = models.DateTimeField(blank=True, null=True)
    client_ip = models.CharField(max_length=512, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    origin = models.CharField(max_length=512, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'public_auth_event'


class PublicAuthGroup(models.Model):
    role = models.CharField(max_length=512, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'public_auth_group'


class PublicAuthMembership(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    group_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'public_auth_membership'


class PublicAuthPermission(models.Model):
    group_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=512, blank=True, null=True)
    table_name = models.CharField(max_length=512, blank=True, null=True)
    record_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'public_auth_permission'


class Qa(models.Model):
    number = models.IntegerField(blank=True, null=True)
    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student')
    programme = models.IntegerField()
    title = models.CharField(max_length=96, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    study_location = models.ForeignKey('StudyLocation', models.DO_NOTHING, db_column='study_location', blank=True, null=True)
    entry_qualification = models.ForeignKey(EntryQualification, models.DO_NOTHING, db_column='entry_qualification', blank=True, null=True)
    reason_for_ending = models.ForeignKey('ReasonForEnding', models.DO_NOTHING, db_column='reason_for_ending', blank=True, null=True)
    dars_upload_date = models.DateField(blank=True, null=True)
    dars_upload_closed = models.BooleanField()
    sits_code = models.CharField(max_length=12, blank=True, null=True)
    candidate_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'qa'


class Qualification(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64, blank=True, null=True)
    is_award = models.BooleanField(blank=True, null=True)
    is_postgraduate = models.BooleanField()
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    on_hesa_return = models.BooleanField(blank=True, null=True)
    hesa_code = models.CharField(max_length=8, blank=True, null=True)
    elq_rank = models.IntegerField(blank=True, null=True)
    is_matriculated = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'qualification'


class ReasonForEnding(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64, blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reason_for_ending'


class ReligionOrBelief(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64, blank=True, null=True)
    web_publish = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'religion_or_belief'


class Room(models.Model):
    id = models.CharField(primary_key=True, max_length=12)
    size = models.IntegerField()
    bookable = models.BooleanField()
    building = models.CharField(max_length=12, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'room'


class RtwDocumentType(models.Model):
    rtw_type = models.ForeignKey('RtwType', models.DO_NOTHING, db_column='rtw_type')
    name = models.CharField(max_length=64, blank=True, null=True)
    display_order = models.IntegerField(blank=True, null=True)
    limited_hours = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'rtw_document_type'


class RtwType(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rtw_type'


class Setting(models.Model):
    name = models.TextField()
    type = models.TextField()
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    academic_year = models.IntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'setting'


class SitsNations(models.Model):
    hesa_nation = models.CharField(max_length=64, blank=True, null=True)
    sits_nation = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sits_nations'
        unique_together = (('hesa_nation', 'sits_nation'),)


class StaffRole(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'staff_role'


class StudentArchive(models.Model):
    husid = models.BigIntegerField(blank=True, null=True)
    source = models.IntegerField(blank=True, null=True)
    target = models.IntegerField(blank=True, null=True)
    json = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=32, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=32, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'student_archive'


class StudentJobTitle(models.Model):
    id = models.AutoField()
    student = models.ForeignKey(Student, models.DO_NOTHING, db_column='student', blank=True, null=True)
    title = models.CharField(max_length=128, blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'student_job_title'


class StudyLocation(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64, blank=True, null=True)
    hesa_code = models.CharField(max_length=8, blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'study_location'


class Subject(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    area = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subject'


class Suspension(models.Model):
    student = models.ForeignKey(Student, models.DO_NOTHING, db_column='student', blank=True, null=True)
    start_date = models.DateField()
    expected_return_date = models.DateField(blank=True, null=True)
    actual_return_date = models.DateField(blank=True, null=True)
    reason = models.IntegerField(blank=True, null=True)
    note = models.CharField(max_length=256, blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'suspension'


class TempAwardData2(models.Model):
    id = models.IntegerField()
    qa = models.IntegerField()
    sits_id = models.CharField(db_column='SITS_ID', max_length=50)  # Field name made lowercase.
    surname = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    birthdate = models.DateTimeField(blank=True, null=True)
    programme_title = models.CharField(max_length=100)
    start_date = models.DateTimeField(blank=True, null=True)
    found_on_dataview = models.CharField(max_length=50)
    comments = models.TextField(db_column='Comments', blank=True, null=True)  # Field name made lowercase.
    row_number_for_sits_id = models.CharField(db_column='row_number_for_SITS_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    row_number_for_surname = models.CharField(max_length=50, blank=True, null=True)
    row_number_for_birthdate = models.CharField(max_length=50, blank=True, null=True)
    evision_student_number = models.CharField(db_column='eVision_student_number', max_length=50, blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=50, blank=True, null=True)  # Field name made lowercase.
    surname2 = models.CharField(db_column='Surname2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    forename_s = models.CharField(db_column='Forename_s', max_length=50, blank=True, null=True)  # Field name made lowercase.
    forename_1 = models.CharField(db_column='Forename_1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    forename_2 = models.CharField(db_column='Forename_2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    forename_3 = models.CharField(db_column='Forename_3', max_length=50, blank=True, null=True)  # Field name made lowercase.
    preferred_name_s = models.CharField(db_column='Preferred_Name_s', max_length=50, blank=True, null=True)  # Field name made lowercase.
    initials = models.CharField(db_column='Initials', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sex = models.CharField(db_column='Sex', max_length=50, blank=True, null=True)  # Field name made lowercase.
    college = models.CharField(db_column='College', max_length=50, blank=True, null=True)  # Field name made lowercase.
    specialism_code = models.CharField(db_column='Specialism_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    specialism = models.CharField(db_column='Specialism', max_length=100, blank=True, null=True)  # Field name made lowercase.
    award_programme_code = models.CharField(db_column='Award_Programme_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    award_programme_title = models.CharField(db_column='Award_Programme_Title', max_length=50, blank=True, null=True)  # Field name made lowercase.
    status_type = models.CharField(db_column='Status_Type', max_length=50, blank=True, null=True)  # Field name made lowercase.
    student_status = models.CharField(db_column='Student_Status', max_length=50, blank=True, null=True)  # Field name made lowercase.
    award_programme_type = models.CharField(db_column='Award_Programme_Type', max_length=50, blank=True, null=True)  # Field name made lowercase.
    programme_group_code = models.CharField(db_column='Programme_Group_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    programme_group_title = models.CharField(db_column='Programme_Group_Title', max_length=50, blank=True, null=True)  # Field name made lowercase.
    department = models.CharField(db_column='Department', max_length=50, blank=True, null=True)  # Field name made lowercase.
    division = models.CharField(db_column='Division', max_length=50, blank=True, null=True)  # Field name made lowercase.
    mode_of_attendance = models.CharField(db_column='Mode_of_Attendance', max_length=50, blank=True, null=True)  # Field name made lowercase.
    previous_college = models.CharField(db_column='Previous_College', max_length=50, blank=True, null=True)  # Field name made lowercase.
    location_of_study = models.CharField(db_column='Location_of_Study', max_length=50, blank=True, null=True)  # Field name made lowercase.
    start_date1 = models.CharField(db_column='Start_Date1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    year_of_programme = models.CharField(db_column='Year_of_Programme', max_length=50, blank=True, null=True)  # Field name made lowercase.
    expected_end_date = models.CharField(db_column='Expected_End_Date', max_length=50, blank=True, null=True)  # Field name made lowercase.
    award_outcome = models.CharField(db_column='Award_Outcome', max_length=50, blank=True, null=True)  # Field name made lowercase.
    end_date = models.CharField(db_column='End_Date', max_length=50, blank=True, null=True)  # Field name made lowercase.
    date_of_last_attendance = models.CharField(db_column='Date_of_Last_Attendance', max_length=50, blank=True, null=True)  # Field name made lowercase.
    reason_for_leaving = models.CharField(db_column='Reason_For_Leaving', max_length=100, blank=True, null=True)  # Field name made lowercase.
    degree_ceremony_date = models.CharField(db_column='Degree_Ceremony_Date', max_length=50, blank=True, null=True)  # Field name made lowercase.
    reason_for_absence = models.CharField(db_column='Reason_for_Absence', max_length=50, blank=True, null=True)  # Field name made lowercase.
    age = models.CharField(db_column='Age', max_length=50, blank=True, null=True)  # Field name made lowercase.
    date_of_birth = models.CharField(db_column='Date_of_Birth', max_length=50, blank=True, null=True)  # Field name made lowercase.
    student_oxford_email = models.CharField(db_column='Student_Oxford_Email', max_length=50, blank=True, null=True)  # Field name made lowercase.
    personal_email = models.CharField(db_column='Personal_Email', max_length=50, blank=True, null=True)  # Field name made lowercase.
    phone_mobile = models.CharField(db_column='Phone_Mobile', max_length=50, blank=True, null=True)  # Field name made lowercase.
    phone_contact = models.CharField(db_column='Phone_Contact', max_length=50, blank=True, null=True)  # Field name made lowercase.
    fee_status = models.CharField(db_column='Fee_Status', max_length=50, blank=True, null=True)  # Field name made lowercase.
    country_of_birth = models.CharField(db_column='Country_of_Birth', max_length=50, blank=True, null=True)  # Field name made lowercase.
    nationality = models.CharField(db_column='Nationality', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dual_nationality = models.CharField(db_column='Dual_Nationality', max_length=50, blank=True, null=True)  # Field name made lowercase.
    domicile = models.CharField(db_column='Domicile', max_length=50, blank=True, null=True)  # Field name made lowercase.
    funding_source = models.CharField(db_column='Funding_Source', max_length=50, blank=True, null=True)  # Field name made lowercase.
    college_advisor_person_number_1 = models.CharField(db_column='College_Advisor_Person_Number_1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    college_advisor_name_1 = models.CharField(db_column='College_Advisor_Name_1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    college_advisor_person_number_2 = models.CharField(db_column='College_Advisor_Person_Number_2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    college_advisor_name_2 = models.CharField(db_column='College_Advisor_Name_2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    oxford_user_id = models.CharField(db_column='Oxford_User_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    card_number = models.CharField(db_column='Card_Number', max_length=50, blank=True, null=True)  # Field name made lowercase.
    husid = models.CharField(db_column='HUSID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    hesa_instance_numhus = models.CharField(db_column='HESA_Instance_NUMHUS', max_length=50, blank=True, null=True)  # Field name made lowercase.
    rhodes_year = models.CharField(db_column='Rhodes_Year', max_length=50, blank=True, null=True)  # Field name made lowercase.
    ucas_number = models.CharField(db_column='UCAS_Number', max_length=50, blank=True, null=True)  # Field name made lowercase.
    ucas_personal_id = models.CharField(db_column='UCAS_Personal_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    student_support_number_slc = models.CharField(db_column='Student_Support_Number_SLC', max_length=50, blank=True, null=True)  # Field name made lowercase.
    term_time_accommodation_type = models.CharField(db_column='Term_Time_Accommodation_Type', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'temp_award_data2'


class TempFeedback(models.Model):
    rate_tutor = models.CharField(max_length=50, blank=True, null=True)
    rate_content = models.CharField(max_length=50, blank=True, null=True)
    rate_admin = models.CharField(max_length=50, blank=True, null=True)
    rate_facilities = models.CharField(max_length=50, blank=True, null=True)
    rate_refreshments = models.CharField(max_length=50, blank=True, null=True)
    rate_accommodation = models.CharField(max_length=50, blank=True, null=True)
    your_name = models.CharField(max_length=250, blank=True, null=True)
    module_id = models.CharField(max_length=50, blank=True, null=True)
    hash_id = models.CharField(max_length=50, blank=True, null=True)
    notified = models.DateTimeField(blank=True, null=True)
    submitted = models.DateTimeField(blank=True, null=True)
    avg_score = models.CharField(max_length=50, blank=True, null=True)
    reminder = models.DateTimeField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'temp_feedback'


class TermsAndConditions(models.Model):
    description = models.CharField(max_length=64)
    url = models.CharField(max_length=256)
    type = models.IntegerField(blank=True, null=True)
    academic_year = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'terms_and_conditions'


class TransactionType(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=32, blank=True, null=True)
    is_cash = models.BooleanField()
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'transaction_type'


class TutorActivity(models.Model):
    id = models.AutoField()
    tutor = models.ForeignKey(Tutor, models.DO_NOTHING, db_column='tutor', blank=True, null=True)
    activity = models.ForeignKey(Activity, models.DO_NOTHING, db_column='activity', blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tutor_activity'


class TutorContract(models.Model):
    tutor_module = models.ForeignKey('TutorModule', models.DO_NOTHING, db_column='tutor_module')
    type = models.CharField(max_length=32)
    options = models.TextField()
    complete = models.BooleanField()
    add_signature = models.BooleanField()
    status = models.ForeignKey('TutorContractStatus', models.DO_NOTHING, db_column='status', blank=True, null=True)
    received = models.BooleanField()
    received_on = models.DateTimeField(blank=True, null=True)
    approver = models.CharField(max_length=32, blank=True, null=True)
    approved_by = models.CharField(max_length=32, blank=True, null=True)
    approved_on = models.DateTimeField(blank=True, null=True)
    signed_by = models.CharField(max_length=32, blank=True, null=True)
    signed_on = models.DateTimeField(blank=True, null=True)
    email_notification = models.CharField(max_length=32, blank=True, null=True)
    created_by = models.CharField(max_length=32)
    created_on = models.DateTimeField()
    modified_by = models.CharField(max_length=32)
    modified_on = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tutor_contract'


class TutorContractSignatory(models.Model):
    name = models.CharField(max_length=64)
    email = models.CharField(max_length=64, blank=True, null=True)
    created_by = models.CharField(max_length=16)
    created_on = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tutor_contract_signatory'


class TutorContractStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    status_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tutor_contract_status'


class TutorFee(models.Model):
    tutor_module = models.ForeignKey('TutorModule', models.DO_NOTHING, db_column='tutor_module')
    amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    type = models.ForeignKey('TutorFeeType', models.DO_NOTHING, db_column='type', blank=True, null=True)
    pay_after = models.DateField(blank=True, null=True)
    raised_by = models.CharField(max_length=50, blank=True, null=True)
    raised_on = models.DateTimeField(blank=True, null=True)
    approved_by = models.CharField(max_length=50, blank=True, null=True)
    approved_on = models.DateTimeField(blank=True, null=True)
    transferred_by = models.CharField(max_length=50, blank=True, null=True)
    transferred_on = models.DateTimeField(blank=True, null=True)
    status = models.ForeignKey('TutorFeeStatus', models.DO_NOTHING, db_column='status')
    details = models.CharField(max_length=500, blank=True, null=True)
    batch = models.IntegerField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    hours_worked = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    weeks = models.IntegerField(blank=True, null=True)
    approver = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tutor_fee'


class TutorFeeRate(models.Model):
    tag = models.CharField(max_length=64, blank=True, null=True)
    amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    type = models.CharField(max_length=64, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tutor_fee_rate'


class TutorFeeStatus(models.Model):
    description = models.CharField(max_length=50, blank=True, null=True)
    paid = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tutor_fee_status'


class TutorFeeType(models.Model):
    description = models.CharField(max_length=64, blank=True, null=True)
    is_hourly = models.BooleanField()
    code = models.CharField(max_length=64, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tutor_fee_type'


class TutorSubject(models.Model):
    tutor = models.ForeignKey(Tutor, models.DO_NOTHING, db_column='tutor', blank=True, null=True)
    subject = models.ForeignKey(Subject, models.DO_NOTHING, db_column='subject', blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=64, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tutor_subject'


class UgApplicationAttachment(models.Model):
    application = models.IntegerField(blank=True, null=True)
    filename = models.CharField(max_length=50, blank=True, null=True)
    attachment = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ug_application_attachment'


class UgApplicationCerthe(models.Model):
    application = models.IntegerField(blank=True, null=True)
    primary_subject = models.CharField(max_length=64, blank=True, null=True)
    secondary_subject = models.CharField(max_length=2048, blank=True, null=True)
    study_mode = models.CharField(max_length=64, blank=True, null=True)
    face_to_face = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ug_application_certhe'


class UgApplicationEntryQualification(models.Model):
    application = models.IntegerField(blank=True, null=True)
    institution = models.CharField(max_length=128, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    qualification = models.CharField(max_length=128, blank=True, null=True)
    subject = models.CharField(max_length=128, blank=True, null=True)
    result = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ug_application_entry_qualification'


class UgApplicationFunding(models.Model):
    application = models.IntegerField(blank=True, null=True)
    source = models.CharField(max_length=256, blank=True, null=True)
    source_details = models.CharField(max_length=256, blank=True, null=True)
    per_year = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    duration = models.CharField(max_length=64, blank=True, null=True)
    status = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ug_application_funding'


class UgApplicationNationality(models.Model):
    application = models.IntegerField()
    nationality = models.IntegerField()
    start_date = models.DateField()
    passport_no = models.CharField(max_length=32, blank=True, null=True)
    country_of_issue = models.IntegerField(blank=True, null=True)
    passport_expiry_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ug_application_nationality'


class UgApplicationOtherQualification(models.Model):
    application = models.IntegerField(blank=True, null=True)
    institution = models.CharField(max_length=128, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    course_title = models.CharField(max_length=128, blank=True, null=True)
    level = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ug_application_other_qualification'


class UgApplicationReferee(models.Model):
    application = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=64, blank=True, null=True)
    firstname = models.CharField(max_length=40, blank=True, null=True)
    surname = models.CharField(max_length=40, blank=True, null=True)
    role = models.CharField(max_length=128, blank=True, null=True)
    address = models.CharField(max_length=512, blank=True, null=True)
    email = models.CharField(max_length=64, blank=True, null=True)
    type = models.CharField(max_length=32, blank=True, null=True)
    requested = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ug_application_referee'


class UgApplicationResidence(models.Model):
    application = models.IntegerField(blank=True, null=True)
    country = models.IntegerField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ug_application_residence'


class UndergraduateApplication(models.Model):
    academic_credit = models.BooleanField(blank=True, null=True)
    title = models.CharField(max_length=20, blank=True, null=True)
    surname = models.CharField(max_length=40, blank=True, null=True)
    previous_surname = models.CharField(max_length=40, blank=True, null=True)
    previous_surname_start = models.DateField(blank=True, null=True)
    previous_surname_end = models.DateField(blank=True, null=True)
    firstname = models.CharField(max_length=40, blank=True, null=True)
    previous_firstname = models.CharField(max_length=40, blank=True, null=True)
    previous_firstname_start = models.DateField(blank=True, null=True)
    previous_firstname_end = models.DateField(blank=True, null=True)
    preferred_name = models.CharField(max_length=40, blank=True, null=True)
    middle_names = models.CharField(max_length=80, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=1, blank=True, null=True)
    birth_country = models.IntegerField(blank=True, null=True)
    nationality = models.IntegerField(blank=True, null=True)
    nationality_start_date = models.DateField(blank=True, null=True)
    dual_national = models.BooleanField(blank=True, null=True)
    other_nationality = models.IntegerField(blank=True, null=True)
    other_nationality_start_date = models.DateField(blank=True, null=True)
    visa_required = models.CharField(max_length=16, blank=True, null=True)
    passport_no = models.CharField(max_length=32, blank=True, null=True)
    country_of_issue = models.IntegerField(blank=True, null=True)
    passport_issue_date = models.DateField(blank=True, null=True)
    passport_expiry_date = models.DateField(blank=True, null=True)
    eu_national_in_uk = models.BooleanField(blank=True, null=True)
    indefinite_leave = models.BooleanField(blank=True, null=True)
    indefinite_leave_date = models.DateField(blank=True, null=True)
    residence = models.IntegerField(blank=True, null=True)
    residence_start_date = models.DateField(blank=True, null=True)
    previous_residence = models.IntegerField(blank=True, null=True)
    previous_residence_start_date = models.DateField(blank=True, null=True)
    previous_residence_end_date = models.DateField(blank=True, null=True)
    address1 = models.CharField(max_length=128, blank=True, null=True)
    address2 = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    county_state = models.CharField(max_length=64, blank=True, null=True)
    postcode = models.CharField(max_length=32, blank=True, null=True)
    native = models.BooleanField(blank=True, null=True)
    entry_qualification = models.CharField(max_length=500, blank=True, null=True)
    entry_qualification_details = models.CharField(max_length=500, blank=True, null=True)
    occupation = models.CharField(max_length=128, blank=True, null=True)
    employer = models.CharField(max_length=128, blank=True, null=True)
    statement = models.CharField(max_length=3000, blank=True, null=True)
    funding = models.CharField(max_length=128, blank=True, null=True)
    invoice_details = models.CharField(max_length=500, blank=True, null=True)
    ethnicity = models.SmallIntegerField(blank=True, null=True)
    religion = models.SmallIntegerField(blank=True, null=True)
    disability = models.CharField(max_length=512, blank=True, null=True)
    disability_details = models.CharField(max_length=128, blank=True, null=True)
    marketing_preferences = models.CharField(max_length=128, blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    email = models.CharField(max_length=64, blank=True, null=True)
    other_email = models.CharField(max_length=64, blank=True, null=True)
    phone = models.CharField(max_length=64, blank=True, null=True)
    english_language_degree = models.BooleanField(blank=True, null=True)
    tier_4_child_visa = models.BooleanField(blank=True, null=True)
    language_test_type = models.CharField(max_length=64, blank=True, null=True)
    language_test_date = models.DateField(blank=True, null=True)
    language_test_result = models.CharField(max_length=128, blank=True, null=True)
    language_test_scores = models.CharField(max_length=128, blank=True, null=True)
    language_test_number = models.CharField(max_length=64, blank=True, null=True)
    test_waiver_request = models.BooleanField(blank=True, null=True)
    referee_name = models.CharField(max_length=50, blank=True, null=True)
    referee_institution = models.CharField(max_length=128, blank=True, null=True)
    referee_email_address = models.CharField(max_length=64, blank=True, null=True)
    attachment_name_1 = models.CharField(max_length=50, blank=True, null=True)
    programme = models.IntegerField()
    is_completed = models.BooleanField(blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=50, blank=True, null=True)
    sexual_orientation = models.CharField(max_length=32, blank=True, null=True)
    gender_identity = models.CharField(max_length=32, blank=True, null=True)
    adult_carer = models.BooleanField(blank=True, null=True)
    child_carer = models.BooleanField(blank=True, null=True)
    uk_secondary = models.CharField(max_length=32, blank=True, null=True)
    free_school_meals = models.CharField(max_length=32, blank=True, null=True)
    parental_undergrad = models.CharField(max_length=32, blank=True, null=True)
    parent_categories_1 = models.CharField(max_length=128, blank=True, null=True)
    parent_categories_2 = models.CharField(max_length=128, blank=True, null=True)
    state_care = models.CharField(max_length=32, blank=True, null=True)
    uk_undergrad = models.CharField(max_length=512, blank=True, null=True)
    undergrad_funding = models.CharField(max_length=512, blank=True, null=True)
    support_needs = models.CharField(max_length=512, blank=True, null=True)
    incomplete_study = models.BooleanField(blank=True, null=True)
    incomplete_study_details = models.CharField(max_length=512, blank=True, null=True)
    concurrent_study = models.BooleanField(blank=True, null=True)
    concurrent_study_details = models.CharField(max_length=512, blank=True, null=True)
    uk_student_loan = models.BooleanField(blank=True, null=True)
    dates_unavailable = models.CharField(max_length=512, blank=True, null=True)
    application = models.IntegerField(blank=True, null=True)
    primary_subject = models.CharField(max_length=64, blank=True, null=True)
    secondary_subject = models.CharField(max_length=2048, blank=True, null=True)
    study_mode = models.CharField(max_length=64, blank=True, null=True)
    face_to_face = models.CharField(max_length=64, blank=True, null=True)
    signature = models.CharField(max_length=128, blank=True, null=True)
    hash = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'undergraduate_application'


class Voucher(models.Model):
    code = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=32, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'voucher'


class VoucherLedger(models.Model):
    voucher = models.ForeignKey(Voucher, models.DO_NOTHING, db_column='voucher')
    ledger = models.ForeignKey(Ledger, models.DO_NOTHING, db_column='ledger')

    class Meta:
        managed = False
        db_table = 'voucher_ledger'
