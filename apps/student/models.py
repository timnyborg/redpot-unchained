from __future__ import annotations

from typing import Optional

from django.db import models
from django.urls import reverse

from apps.core.models import SignatureModel
from apps.invoice.models import Invoice
from apps.module.models import Module

NOT_KNOWN_DOMICILE = 181
NOT_KNOWN_NATIONALITY = 181
NOT_KNOWN_ETHNICITY = 90
# TODO: Make default
NOT_KNOWN_RELIGION = 99


class Student(SignatureModel):
    husid = models.BigIntegerField(blank=True, null=True, verbose_name='HUSID')
    surname = models.CharField(max_length=40)
    firstname = models.CharField(max_length=40)
    title = models.CharField(max_length=20, blank=True, null=True)
    middlename = models.CharField(max_length=40, blank=True, null=True)
    nickname = models.CharField(max_length=64, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    domicile = models.ForeignKey('Domicile', models.DO_NOTHING, db_column='domicile', default=NOT_KNOWN_DOMICILE)
    nationality = models.ForeignKey(
        'Nationality', models.DO_NOTHING, db_column='nationality', default=NOT_KNOWN_NATIONALITY
    )
    ethnicity = models.ForeignKey('Ethnicity', models.DO_NOTHING, db_column='ethnicity', default=NOT_KNOWN_ETHNICITY)
    religion_or_belief = models.IntegerField(default=99)
    occupation = models.CharField(max_length=128, blank=True, null=True)
    termtime_postcode = models.CharField(max_length=32, blank=True, null=True)
    note = models.CharField(max_length=1024, blank=True, null=True)
    no_publicity = models.BooleanField(blank=True, null=True)
    is_flagged = models.BooleanField(default=False)
    is_eu = models.BooleanField(blank=True, null=True)
    deceased = models.BooleanField(db_column='Deceased', blank=True, null=True)  # Field name made lowercase.
    disability = models.ForeignKey('Disability', models.DO_NOTHING, db_column='disability', null=True, blank=True)
    disability_detail = models.CharField(max_length=2048, blank=True, null=True)
    disability_action = models.CharField(max_length=256, blank=True, null=True)
    dars_optout = models.BooleanField(default=True)
    termtime_accommodation = models.IntegerField(blank=True, null=True)
    sits_id = models.IntegerField(blank=True, null=True)
    highest_qualification = models.ForeignKey(
        'qualification_aim.EntryQualification',
        models.DO_NOTHING,
        db_column='highest_qualification',
        limit_choices_to={'web_publish': True},
        blank=True,
        null=True,
    )
    mail_optin = models.BooleanField(default=False)
    mail_optin_on = models.DateTimeField(blank=True, null=True)
    mail_optin_method = models.CharField(max_length=64, blank=True, null=True)
    email_optin = models.BooleanField(default=False)
    email_optin_method = models.CharField(max_length=64, blank=True, null=True)
    email_optin_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'student'

    def __str__(self):
        return f'{self.first_or_nickname} {self.surname}'

    @property
    def first_or_nickname(self):
        if self.nickname:
            return f'{self.nickname} ({self.firstname})'
        return self.firstname

    @property
    def sex(self) -> Optional[int]:
        """Get HESA coding for sex based on gender"""
        gender_to_sex_map = {
            'M': 1,
            'F': 2,
            'I': 3,
        }
        return gender_to_sex_map.get(self.gender or '')

    @property
    def formatdate(self):
        if self.start_date:
            return f'{self.start_date:%d %b %Y}'

    def get_absolute_url(self) -> str:
        return reverse('student-view', args=[self.id])

    def get_edit_url(self):
        return reverse('student:edit', args=[self.id])

    def get_default_address(self) -> Optional[Address]:
        return self.addresses.default().first()

    def get_billing_address(self) -> Optional[Address]:
        return self.addresses.billing().first() or self.get_default_address()

    def get_invoices(self):
        return Invoice.objects.filter(invoice_ledger__ledger__enrolment__qa__student=self).distinct()


class StudentArchive(SignatureModel):
    husid = models.BigIntegerField(blank=True, null=True)
    source = models.IntegerField(blank=True, null=True)
    target = models.IntegerField(blank=True, null=True)
    json = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'student_archive'


class AddressQuerySet(models.QuerySet):
    def default(self) -> models.QuerySet:
        return self.filter(is_default=True)

    def billing(self) -> models.QuerySet:
        return self.filter(is_billing=True)


class Address(SignatureModel):
    # todo: remove the address_type table and convert Address.type to a TextChoice
    class TypeChoices(models.IntegerChoices):
        PERMANENT = 100, "Permanent"
        HOME = 110, 'Home'
        NEXT_OF_KIN = 111, 'Next of Kin'
        COLLEGE = 400, 'College'
        OXFORD_COLLEGE = 410, 'Oxford College'
        WORK = 500, 'Work'
        MANAGER = 510, 'Work - Line Manager'

    student = models.ForeignKey(
        'Student', models.DO_NOTHING, db_column='student', related_name='addresses', related_query_name='address'
    )
    type = models.IntegerField(db_column='type', choices=TypeChoices.choices, default=TypeChoices.PERMANENT)
    line1 = models.CharField(max_length=128)
    line2 = models.CharField(max_length=128, blank=True, null=True)
    line3 = models.CharField(max_length=128, blank=True, null=True)
    town = models.CharField(max_length=64, blank=True, null=True)
    countystate = models.CharField(max_length=64, blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    postcode = models.CharField(max_length=32, blank=True, null=True)
    formatted = models.CharField(max_length=1024, blank=True, null=True)
    is_default = models.BooleanField(default=True)  # todo: figure out default and billing logic.  db or save()?
    is_billing = models.BooleanField(default=False)
    sits_type = models.CharField(max_length=1, blank=True, null=True, editable=False)

    objects = AddressQuerySet.as_manager()

    class Meta:
        db_table = 'address'


class Email(SignatureModel):
    student = models.ForeignKey(
        'Student', models.DO_NOTHING, db_column='student', related_name='emails', related_query_name='email'
    )
    email = models.CharField(max_length=64)
    note = models.CharField(max_length=128, blank=True, null=True)
    is_default = models.BooleanField(default=True)

    class Meta:
        db_table = 'email'


class NextHUSID(models.Model):
    """Tracks how many HUSIDs have been allocated in a given year, acting as a seed for their generation"""

    year = models.IntegerField(primary_key=True)
    next = models.IntegerField(default=0)

    class Meta:
        db_table = 'next_husid'


class MoodleID(SignatureModel):
    moodle_id = models.IntegerField(unique=True)
    student = models.OneToOneField('Student', models.DO_NOTHING, db_column='student', related_name='moodle_id')
    first_module_code = models.CharField(max_length=12)

    class Meta:
        db_table = 'moodle_id'


class OtherID(SignatureModel):
    class Types(models.IntegerChoices):
        STUDENT_CARD = 1
        SSO = 7
        OSS = 8
        SSN = 9

    student = models.ForeignKey(
        'Student',
        models.DO_NOTHING,
        db_column='student',
        related_name='other_ids',
        related_query_name='other_id',
    )
    number = models.CharField(max_length=64, blank=True, null=True)
    type = models.OneToOneField('OtherIdType', models.DO_NOTHING, db_column='type')
    note = models.CharField(max_length=64, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'other_id'


class OtherIdType(models.Model):
    description = models.CharField(max_length=64)

    class Meta:
        db_table = 'other_id_type'


class Nationality(models.Model):
    name = models.CharField(max_length=64)
    is_in_eu = models.BooleanField()
    hesa_code = models.CharField(max_length=8)
    sort_order = models.IntegerField()
    is_active = models.BooleanField()

    class Meta:
        db_table = 'nationality'

    def __str__(self) -> str:
        return str(self.name)


class Domicile(models.Model):
    name = models.CharField(max_length=64)
    is_in_eu = models.BooleanField()
    hesa_code = models.CharField(max_length=8)
    sort_order = models.IntegerField()
    is_active = models.BooleanField()

    class Meta:
        db_table = 'domicile'

    @property
    def is_uk(self) -> bool:
        # Todo: make a UK column
        return self.pk in [240, 241, 242, 243]


class Ethnicity(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        db_table = 'ethnicity'


class Disability(models.Model):
    description = models.CharField(max_length=64, blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    web_publish = models.BooleanField()
    display_order = models.IntegerField(blank=True, null=True)
    custom_description = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'disability'
        unique_together = (('id', 'description', 'custom_description'),)


class Diet(models.Model):
    student = models.OneToOneField('Student', models.DO_NOTHING, db_column='student')
    type = models.ForeignKey('DietType', models.DO_NOTHING, db_column='type', blank=True, null=True)
    note = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        db_table = 'diet'


class DietType(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'diet_type'


class EmergencyContact(SignatureModel):
    student = models.OneToOneField('Student', models.DO_NOTHING, db_column='student', related_name='emergency_contact')
    name = models.CharField(max_length=128, blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    email = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'emergency_contact'


class Phone(SignatureModel):
    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student', related_name="phones")
    type = models.ForeignKey('PhoneType', models.DO_NOTHING, db_column='type')
    number = models.CharField(max_length=64, blank=True, null=True)
    note = models.CharField(max_length=128, blank=True, null=True)
    is_default = models.BooleanField()

    class Meta:
        db_table = 'phone'


class PhoneType(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'phone_type'


class Enquiry(SignatureModel):
    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student', related_name='enquiries')
    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module', related_name='enquiries')
    date = models.DateTimeField(blank=True, null=True)
    detail = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'enquiry'


class Suspension(SignatureModel):
    student = models.ForeignKey(
        'Student', models.DO_NOTHING, db_column='student', related_name="suspensions", blank=True, null=True
    )
    start_date = models.DateField()
    expected_return_date = models.DateField(blank=True, null=True)
    actual_return_date = models.DateField(blank=True, null=True)
    reason = models.IntegerField(blank=True, null=True)
    note = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'suspension'

    def __str__(self) -> str:
        return str(self.name)
