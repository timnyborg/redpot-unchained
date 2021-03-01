from django.db import models
from django.urls import reverse
from apps.core.models import SignatureModel


class Student(SignatureModel):
    husid = models.BigIntegerField(blank=True, null=True, verbose_name='HUSID')
    surname = models.CharField(max_length=40)
    firstname = models.CharField(max_length=40)
    title = models.CharField(max_length=20, blank=True, null=True)
    middlename = models.CharField(max_length=40, blank=True, null=True)
    nickname = models.CharField(max_length=64, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    domicile = models.IntegerField(blank=True, null=True)
    nationality = models.IntegerField(blank=True, null=True)
    ethnicity = models.IntegerField(blank=True, null=True)
    religion_or_belief = models.IntegerField(default=99)
    disability = models.IntegerField(blank=True, null=True)
    occupation = models.CharField(max_length=128, blank=True, null=True)
    termtime_postcode = models.CharField(max_length=32, blank=True, null=True)
    note = models.CharField(max_length=1024, blank=True, null=True)
    no_publicity = models.BooleanField(blank=True, null=True)
    is_flagged = models.BooleanField(default=False)
    is_eu = models.BooleanField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    deceased = models.BooleanField(db_column='Deceased', blank=True, null=True)  # Field name made lowercase.
    disability_detail = models.CharField(max_length=2048, blank=True, null=True)
    disability_action = models.CharField(max_length=256, blank=True, null=True)
    dars_optout = models.BooleanField(default=True)
    termtime_accommodation = models.IntegerField(blank=True, null=True)
    sits_id = models.IntegerField(blank=True, null=True)
    full_name = models.CharField(max_length=82, blank=True, null=True)
    highest_qualification = models.CharField(max_length=128, blank=True, null=True)
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

    def get_absolute_url(self):
        return reverse('student-view', args=[self.id])

    def get_default_address(self):
        return self.addresses.default().first()


class AddressQuerySet(models.QuerySet):
    def default(self):
        return self.filter(is_default=True)

    def billing(self):
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
        'Student', models.DO_NOTHING,
        db_column='student',
        related_name='addresses',
        related_query_name='address'
    )
    type = models.IntegerField(
        db_column='type',
        choices=TypeChoices.choices,
        default=TypeChoices.PERMANENT
    )
    line1 = models.CharField(max_length=128)
    line2 = models.CharField(max_length=128, blank=True, null=True)
    line3 = models.CharField(max_length=128, blank=True, null=True)
    town = models.CharField(max_length=64, blank=True, null=True)
    countystate = models.CharField(max_length=64, blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    postcode = models.CharField(max_length=32, blank=True, null=True)
    formatted = models.CharField(max_length=1024, blank=True, null=True)
    is_default = models.BooleanField()
    is_billing = models.BooleanField(blank=True, null=True)
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


class Email(models.Model):
    student = models.ForeignKey(
        'Student',
        models.DO_NOTHING,
        db_column='student',
        related_name='emails',
        related_query_name='email'
    )
    email = models.CharField(max_length=64)
    note = models.CharField(max_length=128, blank=True, null=True)
    is_default = models.BooleanField(default=True)

    class Meta:
        # managed = False
        db_table = 'email'
