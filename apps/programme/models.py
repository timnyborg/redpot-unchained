from django.db import models
from django.db.models import Model, CharField, DateTimeField, EmailField, BooleanField, IntegerField, DateField, ManyToManyField, DecimalField, ForeignKey, DO_NOTHING, Q
from django.core.validators import MinLengthValidator, RegexValidator
from django.urls import reverse
from django.forms.widgets import TextInput


class PhoneInput(TextInput):
    input_type = 'tel'


class PhoneField(CharField):
    default_validators = [RegexValidator(regex='^[-0-9 +()]+$', message='Invalid phone number')]
    widget = PhoneInput


class Portfolio(Model):
    name = CharField(max_length=128, blank=True, null=True)
    division = ForeignKey('Division', DO_NOTHING, db_column='division', blank=True, null=True)
    email = EmailField(max_length=256, blank=True, null=True)
    phone = CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[app].[portfolio]'
        ordering = ['name']
        
    def __str__(self):
        return self.name
        

class Division(Model):
    name = CharField(max_length=64, blank=True, null=True)
    shortname = CharField(max_length=8, blank=True, null=True)
    email = EmailField(max_length=256, blank=True, null=True)
    finance_prefix = CharField(max_length=2, blank=True, null=True)
    # manager = ForeignKey(AuthUser, DO_NOTHING, db_column='manager', blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[app].[division]'
        ordering = ['name']
        
    def __str__(self):
        return self.name
  

class StudyLocation(Model):
    id = IntegerField(primary_key=True)
    description = CharField(max_length=64, blank=True, null=True)
    hesa_code = CharField(max_length=8, blank=True, null=True)
    created_by = CharField(max_length=16, blank=True, null=True)
    created_on = DateTimeField(blank=True, null=True)
    modified_by = CharField(max_length=16, blank=True, null=True)
    modified_on = DateTimeField(blank=True, null=True)
    is_active = BooleanField()

    class Meta:
        managed = False
        db_table = '[app].[study_location]'
        
    def __str__(self):
        return self.description
  

class Programme(Model):
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

    modules = ManyToManyField('module.Module', through='ProgrammeModule')

    title = CharField(max_length=96, null=True)
    start_date = DateField(blank=True, null=True)
    end_date = DateField(blank=True, null=True)
    division = ForeignKey(Division, DO_NOTHING, db_column='division', limit_choices_to=Q(id__gt=8) | Q(id__lt=5))
    portfolio = ForeignKey(Portfolio, DO_NOTHING, db_column='portfolio')
    qualification = ForeignKey('Qualification', DO_NOTHING, db_column='qualification')
    student_load = DecimalField(max_digits=10, decimal_places=4, blank=True, null=True, help_text='Percent of full-time, eg. 50')
    funding_level = IntegerField(blank=True, null=True, choices=FUNDING_LEVELS)
    funding_source = IntegerField(blank=True, null=True, choices=FUNDING_SOURCES)
    study_mode = IntegerField(blank=True, null=True, choices=STUDY_MODES)
    study_location = ForeignKey(StudyLocation, DO_NOTHING, db_column='study_location', blank=True, null=True)

    is_active = BooleanField(default=True)
    sits_code = CharField(max_length=32, blank=True, null=True)
    contact_list_display = BooleanField(default=True)

    email = EmailField(max_length=64, blank=True, null=True)
    phone = PhoneField(max_length=64, blank=True, null=True)

    created_by = CharField(max_length=8, blank=True, null=True, )
    created_on = DateTimeField(blank=True, null=True, auto_now_add=True)
    modified_by = CharField(max_length=8, blank=True, null=True)
    modified_on = DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = '[app].[programme]'
        permissions = [
            ('edit_registry_fields', 'Can edit programme fields like Study Location or Student Load '
                                     '(should just be one programme.edit permission'),
            ('edit_restricted_fields', 'Can edit dev-restricted fields (is_active, contact_list_display, sits_id'),
        ]
        
    def get_absolute_url(self):
        return reverse('programme:view', args=[self.id])

    def __str__(self):
        return self.title


class ProgrammeModule(Model):
    programme = ForeignKey(Programme, DO_NOTHING, db_column='programme', blank=True, null=True)
    module = ForeignKey('module.Module', DO_NOTHING, db_column='module', blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[app].[programme_module]'
        unique_together = (('programme', 'module'), ('module', 'programme'),)
        
        
class Qualification(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=64, blank=True, null=True)
    is_award = BooleanField(blank=True, null=True)
    is_postgraduate = BooleanField()
    created_by = CharField(max_length=16, blank=True, null=True)
    created_on = DateTimeField(blank=True, null=True)
    modified_by = CharField(max_length=16, blank=True, null=True)
    modified_on = DateTimeField(blank=True, null=True)
    on_hesa_return = BooleanField(blank=True, null=True)
    hesa_code = CharField(max_length=8, blank=True, null=True)
    elq_rank = IntegerField(blank=True, null=True)
    is_matriculated = BooleanField()

    class Meta:
        managed = False
        db_table = '[app].[qualification]'
        ordering = ['elq_rank']
        
    def __str__(self):
        return self.name
        
    def name_with_code(self):
        return f'{self.name} ({self.hesa_code})'
        
        
class Student(models.Model):
    husid = models.BigIntegerField(blank=True, null=True)
    surname = models.CharField(max_length=40, blank=True, null=True)
    firstname = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[app].[student]'
        
    def __str__(self):
        return f'{self.firstname} {self.surname}'
        
        
class QA(models.Model):
    student = models.ForeignKey('Student', models.DO_NOTHING, db_column='student')
    programme = models.IntegerField()
    title = models.CharField(max_length=96, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[app].[qa]'

    @property
    def academic_year(self):
        if self.start_date:
            return self.start_date.year - (1 if self.start_date.month < 8 else 0)


class Enrolment(models.Model):
    qa = models.ForeignKey('Qa', models.DO_NOTHING, db_column='qa', blank=True, null=True)
    module = models.ForeignKey('module.Module', models.DO_NOTHING, db_column='module', related_name='enrolments')
    status = models.ForeignKey('EnrolmentStatus', models.DO_NOTHING, db_column='status')
    result = models.ForeignKey('EnrolmentResult', models.DO_NOTHING, db_column='result')
    points_awarded = models.IntegerField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    provenance = models.IntegerField(blank=True, null=True)
    provenance_details = models.CharField(max_length=128, blank=True, null=True)
    no_image_consent = models.BooleanField(blank=True, null=True)
    mark = models.IntegerField(blank=True, null=True)
    transcript_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[app].[enrolment]'


class EnrolmentResult(models.Model):
    id = models.CharField(primary_key=True, max_length=4)
    description = models.CharField(max_length=128, blank=True, null=True)
    is_active = models.BooleanField()
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    display_order = models.IntegerField(blank=True, null=True)
    hesa_code = models.CharField(max_length=1, blank=True, null=True)
    allow_certificate = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[app].[enrolment_result]'
        
        
class EnrolmentStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64, blank=True, null=True)
    takes_place = models.BooleanField()
    is_debtor = models.BooleanField()
    on_hesa_return = models.BooleanField()

    class Meta:
        managed = False
        db_table = '[app].[enrolment_status]'