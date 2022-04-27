from django.db import models
from django.urls import reverse

from apps.core.models import PhoneField, SignatureModel

AT_PROVIDER_STUDY_LOCATION = 1

CERT_HE_SITS_CODE = 'UR_9A1'


class Programme(SignatureModel):
    FUNDING_LEVELS = [
        (10, 'Undergraduate'),
        (11, 'Long undergraduate'),
        (20, 'Postgraduate taught'),
        (21, 'Long postgraduate taught'),
        (30, 'Postgraduate research'),
        (31, 'Long postgraduate research'),
        (99, 'Not in HESES population'),
    ]

    FUNDING_SOURCES = [
        (1, 'Office for Students'),
        (2, 'HEFCW'),
        (3, 'SFC'),
        (4, 'DfE(NI)'),
        (6, 'Welsh Government DfES (including Welsh for Adults)'),
        (7, 'DfE'),
        (11, 'LEA'),
        (13, 'Welsh Government (WG)'),
        (14, 'Scottish Government - Employability, Skills and Lifelong Learning Directorate'),
        (21, 'Biotechnology & Biological Sciences Research Council (BBSRC)'),
        (22, 'Medical Research Council (MRC)'),
        (23, 'Natural Environment Research Council (NERC)'),
        (24, 'Engineering & Physical Sciences Research Council (EPSRC)'),
        (25, 'Economic & Social Research Council (ESRC)'),
        (26, 'Science & Technology Facilities Council (STFC)'),
        (27, 'Arts & Humanities Research Council (AHRC)'),
        (29, 'Research council - not specified'),
        (31, 'Departments of Health/NHS/Social Care'),
        (32, 'Departments of Social Services'),
        (34, 'Other HM government departments'),
        (35, 'Armed forces'),
        (37, 'Wholly NHS funded'),
        (38, 'Partially NHS funded'),
        (39, 'Education and Skills Funding Agency (ESFA)'),
        (41, 'UK public corporation/nationalised industry'),
        (42, 'UK private industry/commerce'),
        (43, 'UK charity (medical)'),
        (44, 'UK charity (other)'),
        (46, 'EU commission (EC)'),
        (51, 'Overseas government or other overseas organisation'),
        (61, 'Own provider'),
        (65, 'European Research Action Scheme for the Mobility of University Students (ERASMUS)'),
        (71, 'Joint between two sources including a funding council'),
        (72, 'Joint between two bodies excluding a funding council'),
        (81, 'Other funding'),
        (84, 'Multinational organisation (non-UK based)'),
        (91, 'Funded entirely by student tuition fees'),
    ]

    STUDY_MODES = [
        (1, 'Full-time according to Funding Council definitions.'),
        (31, 'Part-time'),
        (64, 'Dormant- previously part-time'),
    ]

    title = models.CharField(max_length=96)
    division = models.ForeignKey(
        'core.Division', models.DO_NOTHING, db_column='division', limit_choices_to={'is_active': True}
    )
    portfolio = models.ForeignKey('core.Portfolio', models.DO_NOTHING, db_column='portfolio')
    qualification = models.ForeignKey('Qualification', models.DO_NOTHING, db_column='qualification')
    student_load = models.DecimalField(
        max_digits=10, decimal_places=4, blank=True, null=True, help_text='Percent of full-time, eg. 50'
    )
    funding_level = models.IntegerField(blank=True, null=True, choices=FUNDING_LEVELS)
    funding_source = models.IntegerField(blank=True, null=True, choices=FUNDING_SOURCES)
    study_mode = models.IntegerField(blank=True, null=True, choices=STUDY_MODES)
    study_location = models.ForeignKey(  # Todo: enforce null constraint on prod db
        'StudyLocation',
        models.DO_NOTHING,
        db_column='study_location',
        default=AT_PROVIDER_STUDY_LOCATION,
        limit_choices_to={'is_active': True},
        null=True,
        blank=True,
    )
    # todo: Why does reporting_year_type exist?  Should be a constant in hesa instance.  Probably irrelevant with HDF
    reporting_year_type = models.IntegerField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    sits_code = models.CharField(max_length=32, blank=True, null=True, verbose_name='SITS code')
    contact_list_display = models.BooleanField(default=True)

    email = models.EmailField(max_length=64, blank=True, null=True)
    phone = PhoneField(max_length=64, blank=True, null=True)

    modules = models.ManyToManyField(
        'module.Module', through='ProgrammeModule', related_name='programmes', related_query_name='programme'
    )

    hecos_subjects = models.ManyToManyField(to='hesa.HECoSSubject', through='hesa.ProgrammeHECoSSubject')

    class Meta:
        db_table = 'programme'
        ordering = ('title',)
        permissions = [
            ('edit_restricted_fields', 'Can edit restricted programme fields (e.g. sits_id)'),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('programme:view', args=[self.id])

    def get_delete_url(self):
        return reverse('programme:delete', args=[self.id])

    @property
    def is_certhe(self) -> bool:
        # Todo: There must be a way to this without hardcoding statuses (old and new certhe)
        return self.sits_code == CERT_HE_SITS_CODE


class ProgrammeModule(models.Model):
    programme = models.ForeignKey(
        Programme,
        models.DO_NOTHING,
        db_column='programme',
        related_name='programme_modules',
        limit_choices_to={'is_active': True},
    )
    module = models.ForeignKey(
        'module.Module', models.DO_NOTHING, db_column='module', related_name='programme_modules'
    )

    class Meta:
        db_table = 'programme_module'
        unique_together = ('programme', 'module')


class Qualification(SignatureModel):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    is_award = models.BooleanField()
    is_postgraduate = models.BooleanField()
    on_hesa_return = models.BooleanField()
    hesa_code = models.CharField(max_length=8)
    elq_rank = models.IntegerField()
    is_matriculated = models.BooleanField()
    data_futures_code = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        db_table = 'qualification'
        ordering = ['elq_rank']

    def __str__(self):
        return str(self.name)

    def name_with_code(self):
        return f'{self.name} ({self.hesa_code})'


class StudyLocation(SignatureModel):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64, blank=True, null=True)
    hesa_code = models.CharField(max_length=8, blank=True, null=True)
    is_active = models.BooleanField()

    class Meta:
        db_table = 'study_location'

    def __str__(self):
        return str(self.description)
