from django.db import models
from apps.main.models import SignatureModel


class TutorManager(models.Manager):
    # Always join in student table
    def get_queryset(self):
        return super().get_queryset().select_related('student')


class Tutor(SignatureModel):
    student = models.OneToOneField('student.Student', models.DO_NOTHING, db_column='student', blank=True, null=True)
    qualifications = models.CharField(max_length=256, blank=True, null=True)
    affiliation = models.CharField(max_length=256, blank=True, null=True)
    nino = models.CharField(max_length=64, blank=True, null=True)
    employee_no = models.CharField(max_length=32, blank=True, null=True)
    appointment_id = models.CharField(max_length=32, blank=True, null=True)
    bankname = models.CharField(max_length=64, blank=True, null=True)
    branchaddress = models.CharField(max_length=128, blank=True, null=True)
    accountname = models.CharField(max_length=64, blank=True, null=True)
    sortcode = models.CharField(max_length=8, blank=True, null=True)
    accountno = models.CharField(max_length=32, blank=True, null=True)
    swift = models.CharField(db_column='SWIFT', max_length=11, blank=True, null=True)  # Field name made lowercase.
    iban = models.CharField(db_column='IBAN', max_length=34, blank=True, null=True)  # Field name made lowercase.
    other_bank_details = models.CharField(max_length=512, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    has_right_to_work_a = models.BooleanField()
    has_right_to_work_b = models.BooleanField()
    image = models.CharField(max_length=255, blank=True, null=True)

    # rtw_type = models.ForeignKey(RtwType, models.DO_NOTHING, db_column='rtw_type', blank=True, null=True)
    # rtw_document_type = models.ForeignKey(RtwDocumentType, models.DO_NOTHING, db_column='rtw_document_type', blank=True, null=True)
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


class TutorModule(SignatureModel):
    module = models.ForeignKey('module.Module', models.DO_NOTHING, db_column='module', related_name='tutor_modules')
    tutor = models.ForeignKey('Tutor', models.DO_NOTHING, db_column='tutor', related_name='tutor_modules')
    role = models.CharField(max_length=64, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    is_published = models.BooleanField(blank=True, null=True)
    image_published = models.IntegerField(blank=True, null=True)
    display_order = models.IntegerField(blank=True, null=True)
    is_teaching = models.BooleanField()
    director_of_studies = models.BooleanField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'tutor_module'
