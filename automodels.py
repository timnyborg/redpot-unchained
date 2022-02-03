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


class ModuleType(models.Model):
    type = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'module_type'


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


class PolarPostcodes(models.Model):
    no_spaces = models.CharField(primary_key=True, max_length=10)
    quintile = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'polar_postcodes'


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


class TermsAndConditions(models.Model):
    description = models.CharField(max_length=64)
    url = models.CharField(max_length=256)
    type = models.IntegerField(blank=True, null=True)
    academic_year = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'terms_and_conditions'
