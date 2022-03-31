# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


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


class TermsAndConditions(models.Model):
    description = models.CharField(max_length=64)
    url = models.CharField(max_length=256)
    type = models.IntegerField(blank=True, null=True)
    academic_year = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'terms_and_conditions'
