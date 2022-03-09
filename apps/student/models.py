from __future__ import annotations

import random
from datetime import date
from typing import Optional

from django.conf import settings
from django.core import validators
from django.core.exceptions import ImproperlyConfigured
from django.db import models, transaction
from django.db.models import QuerySet
from django.urls import reverse

from apps.core.models import AddressModel, SignatureModel, SITSLockingModelMixin
from apps.core.utils.models import PhoneField
from apps.enrolment.models import Enrolment
from apps.invoice.models import Invoice
from apps.module.models import Module

NOT_KNOWN_DOMICILE = 181
NOT_KNOWN_NATIONALITY = 181
NOT_KNOWN_ETHNICITY = 90
NOT_KNOWN_RELIGION = 99
NOT_AVAILABLE_SEXUAL_ORIENTATION = 99
NOT_AVAILABLE_PARENTAL_EDUCATION = 8
NOT_AVAILABLE_GENDER_IDENTITY = 99

MINIMUM_BIRTHDATE = date(1900, 1, 1)


class Student(SITSLockingModelMixin, SignatureModel):
    sits_managed_fields = [
        'firstname',
        'surname',
        'middlename',
        'gender',
        'husid',
        'birthdate',
        'domicile',
        'nationality',
    ]

    class MarketingOptinMethods(models.TextChoices):
        APPLICATION_FORM = (
            'Application form',
            'Application form',
        )
        EMAIL = (
            'Email',
            'Email',
        )
        EMAIL_RESUBSCRIBE = (
            'Email_resubscribe',
            'Email resubscribe link',
        )
        IN_PERSON = (
            'In_person',
            'In-person',
        )
        NEWSLETTER = (
            'Newsletter',
            'Newsletter widget',
        )
        OTHER_FORM = (
            'Other',
            'Other form',
        )
        PHONE = (
            'Phone',
            'Phone',
        )
        WESBITE = 'Website', 'Website optin'

    class Genders(models.TextChoices):
        MALE = ('M', 'Male')
        FEMALE = ('F', 'Female')
        OTHER = ('I', 'Other')
        UNKNOWN = ('', 'Unknown')

    husid = models.BigIntegerField(blank=True, null=True, verbose_name='HESA ID')
    surname = models.CharField(max_length=40)
    firstname = models.CharField(max_length=40, verbose_name='First name')
    title = models.CharField(max_length=20, blank=True, null=True)
    middlename = models.CharField(max_length=40, blank=True, null=True, verbose_name='Middle name(s)')
    nickname = models.CharField(
        max_length=64, blank=True, null=True, help_text='If called something other than first name'
    )
    birthdate = models.DateField(blank=True, null=True, validators=[validators.MinValueValidator(MINIMUM_BIRTHDATE)])
    gender = models.CharField(max_length=1, blank=True, null=True, choices=Genders.choices)
    domicile = models.ForeignKey(
        'Domicile',
        models.DO_NOTHING,
        db_column='domicile',
        default=NOT_KNOWN_DOMICILE,
        limit_choices_to={'is_active': True},
    )
    nationality = models.ForeignKey(
        'Nationality',
        models.DO_NOTHING,
        db_column='nationality',
        default=NOT_KNOWN_NATIONALITY,
        limit_choices_to={'is_active': True},
    )
    ethnicity = models.ForeignKey('Ethnicity', models.DO_NOTHING, db_column='ethnicity', default=NOT_KNOWN_ETHNICITY)
    religion_or_belief = models.ForeignKey(
        'Religion', models.DO_NOTHING, db_column='religion_or_belief', default=NOT_KNOWN_RELIGION
    )
    occupation = models.CharField(max_length=128, blank=True, null=True)
    termtime_postcode = models.CharField(max_length=32, blank=True, null=True)
    note = models.CharField(max_length=1024, blank=True, null=True)
    no_publicity = models.BooleanField(verbose_name='Mail marketing opt-out', blank=True, null=True)
    is_flagged = models.BooleanField(
        default=False, verbose_name='Student flagged', help_text="Put details in the 'note' field"
    )
    is_eu = models.BooleanField(blank=True, null=True, verbose_name='Home/EU?')
    deceased = models.BooleanField(db_column='deceased', default=False)
    disability = models.ForeignKey('Disability', models.DO_NOTHING, db_column='disability', null=True, blank=True)
    disability_detail = models.CharField(max_length=2048, blank=True, null=True)
    disability_action = models.CharField(max_length=256, blank=True, null=True)
    sexual_orientation = models.ForeignKey(
        'SexualOrientation',
        models.DO_NOTHING,
        db_column='sexual_orientation',
        default=NOT_AVAILABLE_SEXUAL_ORIENTATION,
    )
    parental_education = models.ForeignKey(
        'ParentalEducation',
        models.DO_NOTHING,
        db_column='parental_education',
        default=NOT_AVAILABLE_PARENTAL_EDUCATION,
    )
    gender_identity = models.ForeignKey(
        'GenderIdentity',
        models.DO_NOTHING,
        db_column='gender_identity',
        default=NOT_AVAILABLE_GENDER_IDENTITY,
    )
    dars_optout = models.BooleanField(default=True)
    termtime_accommodation = models.IntegerField(blank=True, null=True)
    sits_id = models.IntegerField(blank=True, null=True, verbose_name='SITS ID')
    highest_qualification = models.ForeignKey(
        'qualification_aim.EntryQualification',
        models.DO_NOTHING,
        db_column='highest_qualification',
        limit_choices_to={'web_publish': True},
        blank=True,
        null=True,
    )
    mail_optin = models.BooleanField(default=False, verbose_name='Mail marketing')
    mail_optin_on = models.DateTimeField(blank=True, null=True)
    mail_optin_method = models.CharField(max_length=47, blank=True, null=True, choices=MarketingOptinMethods.choices)
    email_optin = models.BooleanField(default=False, verbose_name='Email marketing')
    email_optin_method = models.CharField(
        max_length=47,
        blank=True,
        null=True,
        choices=MarketingOptinMethods.choices,
        help_text='How did this person sign up to receive marketing email?',
    )
    email_optin_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'student'
        verbose_name = 'Person'
        permissions = [
            ('merge_student', 'Merge student records'),
            ('view_restricted_fields', 'Can View and Edit restricted fields'),
        ]

    def __str__(self):
        return f'{self.first_or_nickname} {self.surname}'

    def save(self, *args, **kwargs) -> None:
        if self.deceased:
            # Prevent any marketing
            self.no_publicity = True
            self.email_optin = False
            self.email_optin_on = None
            self.email_optin_method = None
            self.mail_optin = False
            self.mail_optin_on = None
            self.mail_optin_method = None
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse('student:view', args=[self.id])

    def get_edit_url(self):
        return reverse('student:edit', args=[self.id])

    def get_delete_url(self):
        return reverse('student:delete', args=[self.id])

    @property
    def first_or_nickname(self) -> str:
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

    def get_default_email(self) -> Optional[Email]:
        return self.emails.default().first()

    def get_default_address(self) -> Optional[Address]:
        return self.addresses.default().first()

    def get_billing_address(self) -> Optional[Address]:
        return self.addresses.billing().first() or self.get_default_address()

    def get_invoices(self) -> QuerySet[Invoice]:
        return Invoice.objects.filter(invoice_ledger__ledger__enrolment__qa__student=self).distinct()

    def get_enrolments(self, **kwargs) -> QuerySet[Enrolment]:
        """Conveniently get a student's enrolments, regardless of which qualification_aim"""
        return Enrolment.objects.filter(qa__student=self, **kwargs)

    @transaction.atomic
    def set_billing_address(self, address: Address, *, save: bool = True) -> None:
        """Mark a single address as billing
        Set `save=False` if calling from address.save() to avoid a loop
        """
        if address.student != self:
            raise ValueError('Address does not belong to the student')
        # Cancel out all other addresses as billing
        self.addresses.exclude(id=address.id).update(is_billing=False)
        address.is_billing = True
        if save:
            address.save()

    @transaction.atomic
    def set_default_address(self, address: Address, *, save: bool = True) -> None:
        """Mark a single address as default
        Set `save=False` if calling from address.save() to avoid a loop
        """
        if address.student != self:
            raise ValueError('Address does not belong to the student')
        # Cancel out all other addresses as billing
        self.addresses.exclude(id=address.id).update(is_default=False)
        address.is_default = True
        if save:
            address.save()

    @property
    def is_sits_record(self) -> bool:
        return self.sits_id is not None


class StudentArchive(SignatureModel):
    source = models.IntegerField()
    target = models.IntegerField()
    json = models.JSONField()

    class Meta:
        db_table = 'student_archive'


class AddressQuerySet(models.QuerySet):
    def default(self) -> models.QuerySet:
        return self.filter(is_default=True)

    def billing(self) -> models.QuerySet:
        return self.filter(is_billing=True)


class Address(AddressModel, SITSLockingModelMixin, SignatureModel):
    sits_managed_fields = ['line1', 'line2', 'line3', 'town', 'countystate', 'postcode', 'country']

    # todo: remove the address_type table once unused by legacy apps.  consider converting types from int -> string
    class Types(models.IntegerChoices):
        PERMANENT = 100, 'Permanent'
        HOME = 110, 'Home'
        NEXT_OF_KIN = 111, 'Next of Kin'
        COLLEGE = 400, 'College'
        OXFORD_COLLEGE = 410, 'Oxford College'
        WORK = 500, 'Work'
        MANAGER = 510, 'Work - Line Manager'

    student = models.ForeignKey(
        'Student', models.DO_NOTHING, db_column='student', related_name='addresses', related_query_name='address'
    )
    type = models.IntegerField(db_column='type', choices=Types.choices, default=Types.PERMANENT)
    formatted = models.CharField(max_length=1024, blank=True, null=True, editable=False)  # for queries -> print labels
    is_default = models.BooleanField(default=True, verbose_name='Default?')
    is_billing = models.BooleanField(default=False, verbose_name='Billing?')
    sits_type = models.CharField(max_length=1, blank=True, null=True, editable=False)

    objects = AddressQuerySet.as_manager()

    class Meta:
        db_table = 'address'

    def __str__(self) -> str:
        return f'{self.line1}, {self.town}'.strip(',')

    def save(self, *args, **kwargs):
        self.formatted = self.get_formatted()
        # Enforce single-object-limit on billing and default addresses
        if self.is_default:
            self.student.set_default_address(address=self, save=False)
        if self.is_billing:
            self.student.set_billing_address(address=self, save=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """If deleting the default address, make the most recently updated the default"""
        super().delete(*args, **kwargs)
        if self.is_default:
            new_default = self.student.addresses.order_by('-modified_on').first()
            if new_default:
                new_default.is_default = True
                new_default.save()

    def get_absolute_url(self) -> str:
        return self.student.get_absolute_url() + '#addresses'

    def get_edit_url(self) -> str:
        return reverse('student:address:edit', kwargs={'pk': self.pk})

    def get_delete_url(self) -> str:
        return reverse('student:address:delete', kwargs={'pk': self.pk})

    @property
    def is_sits_record(self) -> bool:
        """Determine whether the object originates in SITS"""
        return self.created_by == 'SITS' or self.modified_by == 'SITS' or self.sits_type is not None


class EmailQuerySet(models.QuerySet):
    def default(self) -> models.QuerySet:
        return self.filter(is_default=True)


class Email(SITSLockingModelMixin, SignatureModel):
    sits_managed_fields = ['email']
    student = models.ForeignKey(
        'Student', models.DO_NOTHING, db_column='student', related_name='emails', related_query_name='email'
    )
    email = models.EmailField(max_length=64)
    note = models.CharField(max_length=128, blank=True, null=True)
    is_default = models.BooleanField(default=False, verbose_name='Default?')

    objects = EmailQuerySet.as_manager()

    class Meta:
        db_table = 'email'

    def get_absolute_url(self) -> str:
        return self.student.get_absolute_url() + '#email'

    def get_edit_url(self):
        return reverse('student:email:edit', kwargs={'pk': self.pk})

    def get_delete_url(self) -> str:
        return reverse('student:email:delete', kwargs={'pk': self.pk})

    @property
    def is_sits_record(self) -> bool:
        return self.created_by == 'SITS' or self.modified_by == 'SITS'


class NextHUSID(models.Model):
    """Tracks how many HUSIDs have been allocated in a given year, acting as a seed for their generation"""

    year = models.IntegerField(primary_key=True)
    next = models.IntegerField(default=0)

    class Meta:
        db_table = 'next_husid'


class MoodleID(SignatureModel):
    moodle_id = models.IntegerField(
        unique=True, error_messages={'unique': 'Moodle ID already in use'}, verbose_name='Moodle ID'
    )  # todo: rename this field
    student = models.OneToOneField('Student', models.DO_NOTHING, db_column='student', related_name='moodle_id')
    first_module_code = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        db_table = 'moodle_id'
        verbose_name = 'Moodle ID'

    def get_absolute_url(self) -> str:
        return self.student.get_absolute_url() + '#other_ids'

    def get_edit_url(self) -> str:
        return reverse('student:moodle-id:edit', kwargs={'pk': self.pk})

    def get_delete_url(self) -> str:
        return reverse('student:moodle-id:delete', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        return str(self.moodle_id)

    @property
    def initial_password(self) -> str:
        """Create an initial password for new accounts, which must be changed on login"""
        if not settings.MOODLE_PASSWORD_COMPONENTS:
            raise ImproperlyConfigured('To generate passwords, MOODLE_PASSWORD_COMPONENTS must be set')
        random.seed(str(self.moodle_id) + self.first_module_code)
        password = '-'.join(
            random.choice(settings.MOODLE_PASSWORD_COMPONENTS) for i in range(settings.MOODLE_PASSWORD_COMPONENT_COUNT)
        )
        return password


class OtherID(SITSLockingModelMixin, SignatureModel):
    sits_managed_fields = ['type', 'number']

    class Types(models.IntegerChoices):
        STUDENT_CARD = 1
        SSO = 7
        OSS = 8
        SSN = 9

    class OtherIdTypeChoices(models.IntegerChoices):
        STUDENT_BAR_CODE_ID = 1, 'Student Bar code ID'
        PASSPORT_ID = 2, 'Passport ID'
        VISA_ID = 3, 'Visa ID'
        HESA_ID = 4, 'HESA ID'
        GMC = 5, 'Regulatory Body Ref. Number (eg. GMC)'
        ULN = 6, 'Unique Learner Number (ULN)'
        SSO = 7, 'SSO username'
        OSS = 8, 'OSS person number'
        STUDENT_SUPPORT_NUM = 9, 'Student support number'
        ALUMNI_NUM = 10, 'Alumni number'
        __empty__ = ' –– Choose one –– '

    student = models.ForeignKey(
        'Student',
        models.DO_NOTHING,
        db_column='student',
        related_name='other_ids',
        related_query_name='other_id',
    )
    number = models.CharField(max_length=64)
    type = models.IntegerField(choices=OtherIdTypeChoices.choices)
    note = models.CharField(max_length=64, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'other_id'
        verbose_name = 'Other ID'

    def __str__(self) -> str:
        return f'{self.get_type_display()}: {self.number}'

    def get_absolute_url(self) -> str:
        return self.student.get_absolute_url() + '#other_ids'

    def get_edit_url(self):
        return reverse('student:other-id:edit', kwargs={'pk': self.pk})

    def get_delete_url(self) -> str:
        return reverse('student:other-id:delete', kwargs={'pk': self.pk})

    @property
    def is_sits_record(self) -> bool:
        return self.created_by == 'SITS' or self.modified_by == 'SITS'


class Nationality(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    is_in_eu = models.BooleanField()
    hesa_code = models.CharField(max_length=8)
    sort_order = models.IntegerField()
    is_active = models.BooleanField()

    class Meta:
        db_table = 'nationality'
        ordering = ('sort_order', 'name')

    def __str__(self) -> str:
        return str(self.name)


class Domicile(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    is_in_eu = models.BooleanField(default=False)
    hesa_code = models.CharField(max_length=8)
    sort_order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    in_uk = models.BooleanField(default=False)

    class Meta:
        db_table = 'domicile'
        ordering = ('sort_order', 'name')

    def __str__(self) -> str:
        return str(self.name)


class Ethnicity(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=32)

    class Meta:
        db_table = 'ethnicity'
        ordering = ('name',)

    def __str__(self) -> str:
        return str(self.name)


class Disability(SignatureModel):
    description = models.CharField(max_length=64, blank=True, null=True)
    web_publish = models.BooleanField()
    display_order = models.IntegerField(blank=True, null=True)
    custom_description = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'disability'
        ordering = ('display_order', 'description')
        unique_together = (('id', 'description', 'custom_description'),)

    def __str__(self) -> str:
        return str(self.custom_description or self.description)


class Diet(models.Model):
    class Types(models.IntegerChoices):
        VEGETARIAN = 200, "Vegetarian"
        VEGAN = 210, "Vegan"
        FISH_EATING_VEGETARIAN = 220, "Fish-eating vegetarian"
        DEMI_VEGETARIAN = 230, "Demi-vegetarian (no red meat)"
        NON_DAIRY = 240, "Non-dairy"
        DIABETIC = 250, "Diabetic"
        GLUTEN_FREE = 320, "Gluten Free (Coeliac)"
        OTHER = 900, "Other"
        __empty__ = 'None'

    student = models.OneToOneField('Student', models.DO_NOTHING, db_column='student')
    type = models.IntegerField(
        choices=Types.choices, db_column='type', blank=True, null=True, verbose_name='Special diet'
    )
    note = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        db_table = 'diet'

    def __str__(self) -> str:
        return f'{self.get_type_display()}: {self.note}'


class EmergencyContact(SignatureModel):
    student = models.OneToOneField('Student', models.DO_NOTHING, db_column='student', related_name='emergency_contact')
    name = models.CharField(max_length=128)
    phone = PhoneField(max_length=32, blank=True, null=True)
    email = models.EmailField(max_length=128, blank=True, null=True)

    class Meta:
        db_table = 'emergency_contact'

    def get_delete_url(self) -> str:
        return reverse('student:emergency-contact:delete', kwargs={'pk': self.pk})


class Phone(SITSLockingModelMixin, SignatureModel):
    sits_managed_fields = ['type', 'number']

    class PhoneTypeChoices(models.IntegerChoices):
        PHONE = 100, 'Phone'
        ALT_PHONE = 110, 'Alternative phone!'
        MOBILE = 120, 'Mobile'
        FAX = 130, 'Fax'
        EMAIL = 200, 'Email'
        INVALID = 299, 'Invalid'
        __empty__ = ' –– Choose one –– '

    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student', related_name="phones")
    type = models.IntegerField(choices=PhoneTypeChoices.choices, default=PhoneTypeChoices.PHONE)
    number = PhoneField(max_length=64)
    note = models.CharField(max_length=128, blank=True, null=True)
    is_default = models.BooleanField(default=False, verbose_name='Default?')

    class Meta:
        db_table = 'phone'

    def __str__(self) -> str:
        return str(self.number)

    def get_absolute_url(self) -> str:
        return self.student.get_absolute_url() + '#phone'

    def get_edit_url(self):
        return reverse('student:phone:edit', kwargs={'pk': self.pk})

    def get_delete_url(self) -> str:
        return reverse('student:phone:delete', kwargs={'pk': self.pk})

    @property
    def is_sits_record(self) -> bool:
        return self.created_by == 'SITS' or self.modified_by == 'SITS'


class Enquiry(SignatureModel):
    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student', related_name='enquiries')
    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module', related_name='enquiries')
    date = models.DateTimeField(blank=True, null=True)
    detail = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'enquiry'


class Religion(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    web_publish = models.BooleanField(default=True)

    class Meta:
        db_table = 'religion_or_belief'
        ordering = ('name',)

    def __str__(self) -> str:
        return str(self.name)


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


class SexualOrientation(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        db_table = 'sexual_orientation'

    def __str__(self) -> str:
        return str(self.name)


class ParentalEducation(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        db_table = 'parental_education'

    def __str__(self) -> str:
        return str(self.name)


class GenderIdentity(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        db_table = 'gender_identity'

    def __str__(self) -> str:
        return str(self.name)
