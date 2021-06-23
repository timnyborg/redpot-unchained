# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AcornPostcodes(models.Model):
    postcode = models.CharField(max_length=16)
    no_spaces = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = 'acorn_postcodes'


class TutorActivity(models.Model):
    description = models.CharField(max_length=128, blank=True, null=True)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'activity'


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


class CourseApplicationAttachment(models.Model):
    application_id = models.IntegerField(blank=True, null=True)
    filename = models.CharField(max_length=50, blank=True, null=True)
    attachment = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'course_application_attachment'


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


class Division(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    shortname = models.CharField(max_length=8, blank=True, null=True)
    email = models.CharField(max_length=256, blank=True, null=True)
    finance_prefix = models.CharField(max_length=2, blank=True, null=True)
    manager = models.ForeignKey(AuthUser, models.DO_NOTHING, db_column='manager', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'division'


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


class ModuleStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64, blank=True, null=True)
    publish = models.BooleanField(blank=True, null=True)
    short_desc = models.CharField(max_length=50, blank=True, null=True)
    waiting_list = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_status'


class ModuleType(models.Model):
    type = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'module_type'


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
    entry_qualification = models.ForeignKey(
        EntryQualification, models.DO_NOTHING, db_column='entry_qualification', blank=True, null=True
    )
    fees = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    domicile = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment_item'


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
