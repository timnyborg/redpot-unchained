from django.core import validators
from django.db import models
from django.urls import reverse

from apps.core.models import SignatureModel


class TutorManager(models.Manager):
    # Always join in the personal record
    def get_queryset(self):
        return super().get_queryset().select_related('student')


class RightToWorkType(models.IntegerChoices):
    PERMANENT = (1, 'List A (permanent)')
    LIMITED = (2, 'List B (limited)')
    PRE_1997 = (3, 'Started pre-1997')
    OVERSEAS = (4, 'Working overseas - RTW not required')


class Tutor(SignatureModel):
    student = models.OneToOneField('student.Student', models.DO_NOTHING, db_column='student')
    qualifications = models.CharField(max_length=256, blank=True, null=True)
    affiliation = models.CharField(max_length=256, blank=True, null=True)

    nino = models.CharField(
        max_length=64, blank=True, null=True, verbose_name='National insurance #', help_text='Enter without spaces'
    )
    employee_no = models.CharField(max_length=32, blank=True, null=True, verbose_name='Employee #')
    appointment_id = models.CharField(max_length=32, blank=True, null=True, verbose_name='Appointment ID')
    bankname = models.CharField(max_length=64, blank=True, null=True, verbose_name='Bank name')
    branchaddress = models.CharField(max_length=128, blank=True, null=True, verbose_name='Branch address')
    accountname = models.CharField(max_length=64, blank=True, null=True, verbose_name='Account name')
    sortcode = models.CharField(
        max_length=8,
        blank=True,
        null=True,
        verbose_name='Sort code',
        validators=[validators.RegexValidator(r'(\d{6}|\d\d-\d\d-\d\d)', 'Must be in the form 12-34-56 or 123456')],
    )
    accountno = models.CharField(max_length=32, blank=True, null=True, verbose_name='Account #')
    swift = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name='SWIFT',
        help_text='Enter without spaces',
        validators=[validators.RegexValidator(r'^[A-z]{6}[A-z\d]{2,5}$', 'Must be in the form ABCDEF12')],
    )
    iban = models.CharField(
        max_length=34,
        blank=True,
        null=True,
        verbose_name='IBAN',
        help_text='Enter without spaces',
        validators=[
            validators.RegexValidator(r'^[A-z]{2}\d{2}[A-z\d]{4}\d{7,20}$', 'Must be in the form AB12CDEF3456789')
        ],
    )
    other_bank_details = models.CharField(max_length=512, blank=True, null=True, help_text='E.g. routing numbers')
    oracle_supplier_number = models.IntegerField(blank=True, null=True)

    biography = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True)

    # todo: longterm - move rtw data into a one-to-one table (easier permissioning)
    rtw_type = models.IntegerField(
        choices=RightToWorkType.choices, db_column='rtw_type', blank=True, null=True, verbose_name='List'
    )
    rtw_document_type = models.ForeignKey(
        'RightToWorkDocumentType',
        models.DO_NOTHING,
        db_column='rtw_document_type',
        blank=True,
        null=True,
        verbose_name='Document type',
    )
    rtw_check_on = models.DateField(blank=True, null=True, verbose_name='Date check done')
    rtw_check_by = models.CharField(max_length=50, blank=True, null=True, verbose_name='Check done by')
    rtw_start_date = models.DateField(blank=True, null=True, verbose_name='Document issued on')
    rtw_end_date = models.DateField(blank=True, null=True, verbose_name='Document valid until')

    modules = models.ManyToManyField(
        'module.Module',
        related_name='tutors',
        through='TutorModule',
    )

    objects = TutorManager()

    class Meta:
        # managed = False
        db_table = 'tutor'
        permissions = [('edit_bank_details', 'Can view and edit a tutor\'s banking details')]

    def __str__(self):
        return str(self.student)

    def get_absolute_url(self):
        return self.student.get_absolute_url()

    def clean(self):
        # No dashes in sortcode, and upper case other fields
        if self.sortcode:
            self.sortcode = self.sortcode.replace('-', '')
        if self.swift:
            self.swift = self.swift.upper()
        if self.iban:
            self.iban = self.iban.upper()


class TutorModule(SignatureModel):
    module = models.ForeignKey(
        'module.Module',
        models.DO_NOTHING,
        db_column='module',
        related_name='tutor_modules',
        related_query_name='tutor_module',
    )
    tutor = models.ForeignKey(
        'Tutor', models.DO_NOTHING, db_column='tutor', related_name='tutor_modules', related_query_name='tutor_module'
    )
    role = models.CharField(max_length=64, blank=True, help_text="e.g. 'Tutor' or 'Speaker'")
    biography = models.TextField(
        blank=True, null=True, help_text='When filled, this overrides the default tutor biography for this module only'
    )
    is_published = models.BooleanField(default=False, help_text="Display on the website?")
    display_order = models.IntegerField(blank=True, null=True)
    is_teaching = models.BooleanField(
        default=True,
        verbose_name='Is this person teaching or speaking on the course?',
        help_text='i.e. not a course director or demonstrator',
    )
    director_of_studies = models.BooleanField(
        default=False,
        verbose_name='Director of studies / course director',
        help_text='Feedback results will be sent to director automatically',
    )

    class Meta:
        # managed = False
        db_table = 'tutor_module'
        verbose_name = 'Tutor on module'

    def __str__(self):
        person = self.tutor.student
        return f'{person.firstname} {person.surname} on {self.module.title} ({self.module.code})'

    def get_absolute_url(self):
        return reverse('tutor:module:view', args=[self.pk])

    def get_edit_url(self):
        return reverse('tutor:module:edit', args=[self.pk])


class RightToWorkDocumentType(models.Model):
    rtw_type = models.IntegerField(choices=RightToWorkType.choices, db_column='rtw_type')
    name = models.CharField(max_length=64)
    display_order = models.IntegerField(default=0)
    limited_hours = models.BooleanField()

    class Meta:
        db_table = 'rtw_document_type'

    def __str__(self) -> str:
        return str(self.name)
