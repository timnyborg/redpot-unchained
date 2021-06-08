from django.db import models
from django.urls import reverse

from apps.core.models import SignatureModel


class TutorManager(models.Manager):
    # Always join in the personal record
    def get_queryset(self):
        return super().get_queryset().select_related('student')


class Tutor(SignatureModel):
    student = models.OneToOneField('student.Student', models.DO_NOTHING, db_column='student')
    qualifications = models.CharField(max_length=256, blank=True, null=True)
    affiliation = models.CharField(max_length=256, blank=True, null=True)
    nino = models.CharField(max_length=64, blank=True, null=True)
    employee_no = models.CharField(max_length=32, blank=True, null=True)
    appointment_id = models.CharField(max_length=32, blank=True, null=True)

    # todo: longterm - move banking data into a one-to-one table (easier permissioning)
    bankname = models.CharField(max_length=64, blank=True, null=True)
    branchaddress = models.CharField(max_length=128, blank=True, null=True)
    accountname = models.CharField(max_length=64, blank=True, null=True)
    sortcode = models.CharField(max_length=8, blank=True, null=True)
    accountno = models.CharField(max_length=32, blank=True, null=True)
    swift = models.CharField(max_length=11, blank=True, null=True)  # Field name made lowercase.
    iban = models.CharField(max_length=34, blank=True, null=True)  # Field name made lowercase.
    other_bank_details = models.CharField(max_length=512, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)

    # todo: longterm - move rtw data into a one-to-one table (easier permissioning)
    # rtw_type = models.ForeignKey(RtwType, models.DO_NOTHING, db_column='rtw_type', blank=True, null=True)
    # rtw_document_type = models.ForeignKey(
    #     RtwDocumentType, models.DO_NOTHING,
    #     db_column='rtw_document_type',
    #     blank=True, null=True
    # )
    rtw_check_on = models.DateField(blank=True, null=True)
    rtw_check_by = models.CharField(max_length=50, blank=True, null=True)
    rtw_start_date = models.DateField(blank=True, null=True)
    rtw_end_date = models.DateField(blank=True, null=True)
    oracle_supplier_number = models.IntegerField(blank=True, null=True)

    modules = models.ManyToManyField(
        'module.Module',
        related_name='tutors',
        through='TutorModule',
    )

    objects = TutorManager()

    class Meta:
        # managed = False
        db_table = 'tutor'
        # unique_together = (('id', 'student'),)

    def __str__(self):
        return str(self.student)

    def get_absolute_url(self):
        return self.student.get_absolute_url()


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
