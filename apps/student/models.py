from __future__ import annotations

from typing import Optional

from django.db import models
from django.urls import reverse

from apps.core.models import SignatureModel

NOT_KNOWN_DOMICILE = 181
NOT_KNOWN_NATIONALITY = 181
NOT_KNOWN_ETHNICITY = 99
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
    ethnicity = models.IntegerField(blank=True, null=True)
    religion_or_belief = models.IntegerField(default=99)
    disability = models.IntegerField(blank=True, null=True)
    occupation = models.CharField(max_length=128, blank=True, null=True)
    termtime_postcode = models.CharField(max_length=32, blank=True, null=True)
    note = models.CharField(max_length=1024, blank=True, null=True)
    no_publicity = models.BooleanField(blank=True, null=True)
    is_flagged = models.BooleanField(default=False)
    is_eu = models.BooleanField(blank=True, null=True)
    deceased = models.BooleanField(db_column='Deceased', blank=True, null=True)  # Field name made lowercase.
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
        # managed = False
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
        return gender_to_sex_map.get(self.gender)

    def get_absolute_url(self) -> str:
        return reverse('student-view', args=[self.id])

    def get_default_address(self) -> Optional[Address]:
        return self.addresses.default().first()

    def get_billing_address(self) -> Optional[Address]:
        return self.addresses.billing().first() or self.get_default_address()


class AddressQuerySet(models.QuerySet):
    def default(self) -> models.QuerySet:
        return self.filter(is_default=True)

    def billing(self) -> models.QuerySet:
        return self.filter(is_billing=True)


class Address(SignatureModel):
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
        # managed = False
        db_table = 'address'


# todo: remove this table and convert Address.type to a TextChoice
# class AddressType(models.Model):
#     description = models.CharField(max_length=128)
#
#     class Meta:
#         # managed = False
#         db_table = 'address_type'
#
#     def __str__(self):
#         return self.description


class Email(SignatureModel):
    student = models.ForeignKey(
        'Student', models.DO_NOTHING, db_column='student', related_name='emails', related_query_name='email'
    )
    email = models.CharField(max_length=64)
    note = models.CharField(max_length=128, blank=True, null=True)
    is_default = models.BooleanField(default=True)

    class Meta:
        # managed = False
        db_table = 'email'


class NextHUSID(models.Model):
    """Tracks how many HUSIDs have been allocated in a given year, acting as a seed for their generation"""

    year = models.IntegerField(primary_key=True)
    next = models.IntegerField(default=0)

    class Meta:
        # managed = False
        db_table = 'next_husid'


class MoodleID(SignatureModel):
    moodle_id = models.IntegerField(unique=True)
    student = models.OneToOneField('Student', models.DO_NOTHING, db_column='student', related_name='moodle_id')
    first_module_code = models.CharField(max_length=12)

    class Meta:
        # managed = False
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
    type = models.IntegerField(choices=Types.choices)
    note = models.CharField(max_length=64, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'other_id'


class Nationality(models.Model):
    name = models.CharField(max_length=64)
    is_in_eu = models.BooleanField()
    hesa_code = models.CharField(max_length=8)
    sort_order = models.IntegerField()
    is_active = models.BooleanField()

    class Meta:
        # managed = False
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
        # managed = False
        db_table = 'domicile'

    @property
    def is_uk(self) -> bool:
        # Todo: make a UK column
        return self.pk in [240, 241, 242, 243]

    def __str__(self) -> str:
        return str(self.name)
