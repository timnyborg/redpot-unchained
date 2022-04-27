"""
For the (2022-23) definitions, see https://codingmanual.hesa.ac.uk/22056/dataDictionary
"""
from datetime import datetime
from typing import Iterable

from django.db import models

INSTITUTION_CODE = 10007774  # our UKPRN


class XMLStagingModel:
    xml_fields: Iterable[str] = ()
    xml_required: Iterable[str] = ()

    @property
    def element_name(self) -> str:
        """The element produced when generating an XML node from the model.  Defaults to the class name, but
        Can be overridden"""
        return self.__class__.__name__

    def children(self) -> list[models.QuerySet]:
        """Returns a list of querysets, which will be iterated over in sequence to create child nodes"""
        return []


class Batch(XMLStagingModel, models.Model):
    academic_year = models.IntegerField()
    created_on = models.DateTimeField(default=datetime.now)
    created_by = models.CharField(max_length=32, blank=True, null=True)
    filename = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        db_table = 'data_futures_batch'

    def children(self) -> list[models.QuerySet]:
        return [
            self.course_set.all(),
            self.module_set.all(),
            self.qualification_set.all(),
            self.sessionyear_set.all(),
            self.student_set.all(),
            self.venue_set.all(),
        ]


class Course(XMLStagingModel, models.Model):
    xml_fields = ['courseid', 'clsdcrs', 'coursetitle', 'prerequisite', 'qualid', 'ttcid']

    # structure
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE)

    # values
    courseid = models.CharField(max_length=50)
    clsdcrs = models.CharField(max_length=2, default='02')  # we don't have closed courses
    coursetitle = models.CharField(max_length=255)
    prerequisite = models.CharField(max_length=2)  # ug vs pg
    qualid = models.CharField(max_length=50)  # fk to qualification
    ttcid = models.CharField(max_length=2, default='07')  # No teacher training courses

    class Meta:
        db_table = 'data_futures_course'

    def children(self) -> list[models.QuerySet]:
        return [self.courserole_set.all()]


class CourseRole(XMLStagingModel, models.Model):
    xml_fields = ['hesaid', 'roletype', 'crproportion']

    # structure
    course = models.ForeignKey('Course', on_delete=models.CASCADE)

    # values
    hesaid = models.IntegerField(default=INSTITUTION_CODE)
    roletype = models.IntegerField(default=202)  # delivery organization
    crproportion = models.IntegerField(default=100)

    class Meta:
        db_table = 'data_futures_course_role'


class Module(XMLStagingModel, models.Model):
    xml_fields = ['modid', 'crdtpts', 'crdtscm', 'fte', 'levlpts', 'mtitle']

    # structure
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE)

    # values
    modid = models.CharField(max_length=50)
    crdtpts = models.IntegerField()
    crdtscm = models.CharField(max_length=2, default='01')  # cats
    fte = models.DecimalField(max_digits=4, decimal_places=1)
    levlpts = models.IntegerField(null=True)  # apparently optional!
    mtitle = models.CharField(max_length=255)

    class Meta:
        db_table = 'data_futures_module'

    def children(self) -> list[models.QuerySet]:
        return [self.modulecostcentre_set.all(), self.modulesubject_set.all()]


# todo: amend core module and subject data structure, so cost centres are allocated directly to modules
class ModuleCostCentre(XMLStagingModel, models.Model):
    xml_fields = ['costcn', 'costcnproportion']

    # structure
    module = models.ForeignKey('Module', on_delete=models.CASCADE)

    # values
    costcn = models.IntegerField(null=True)  # null while we're relying on hecos subjects for cost centres
    costcnproportion = models.IntegerField()

    class Meta:
        db_table = 'data_futures_module_cost_centre'


class ModuleSubject(XMLStagingModel, models.Model):
    xml_fields = ['modsbj', 'modproportion']

    # structure
    module = models.ForeignKey('Module', on_delete=models.CASCADE)

    # values
    modsbj = models.IntegerField()  # hecos value
    modproportion = models.IntegerField()

    class Meta:
        db_table = 'data_futures_module_subject'


class Qualification(XMLStagingModel, models.Model):
    xml_fields = ['qualid', 'qualcat']

    # structure
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE)

    # values
    qualid = models.CharField(max_length=50)
    qualcat = models.CharField(max_length=5)  # qualification.data_futures_code

    class Meta:
        db_table = 'data_futures_qualification'

    def children(self) -> list[models.QuerySet]:
        return [self.awardingbodyrole_set.all(), self.qualificationsubject_set.all()]


class AwardingBodyRole(XMLStagingModel, models.Model):
    xml_fields = ['awardingbodyid']

    # structure
    qualification = models.ForeignKey('Qualification', on_delete=models.CASCADE)

    # values
    awardingbodyid = models.IntegerField(default=INSTITUTION_CODE)

    class Meta:
        db_table = 'data_futures_awarding_body_role'


class QualificationSubject(XMLStagingModel, models.Model):
    xml_fields = ['qualsubject', 'qualproportion']

    # structure
    qualification = models.ForeignKey('Qualification', on_delete=models.CASCADE)

    # values
    qualsubject = models.IntegerField()  # hecos value
    qualproportion = models.IntegerField()

    class Meta:
        db_table = 'data_futures_qualification_subject'


class SessionYear(XMLStagingModel, models.Model):
    xml_fields = ['sessionyearid', 'syenddate', 'systartdate']

    # structure
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE)

    # values
    sessionyearid = models.CharField(max_length=50)
    syenddate = models.DateField()
    systartdate = models.DateField()

    class Meta:
        db_table = 'data_futures_session_year'


class Student(XMLStagingModel, models.Model):
    xml_fields = [
        'sid',
        'birthdte',
        'ethnic',
        'fnames',
        'genderid',
        'nation',
        'ownstu',
        'religion',
        'sexid',
        'sexort',
        'ssn',
        'surname',
        'ttaccom',
        'ttpcode',
    ]

    # structure
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE)

    # values
    sid = models.CharField(max_length=17)  # todo: slightly different than husid, will need generating
    birthdte = models.DateField(null=True)
    ethnic = models.IntegerField(null=True)
    fnames = models.CharField(max_length=100)
    genderid = models.CharField(max_length=2)
    nation = models.CharField(max_length=2)  # todo: Not Known value appears changed
    ownstu = models.IntegerField()
    religion = models.IntegerField()
    sexid = models.IntegerField()
    sexort = models.IntegerField()
    ssn = models.CharField(max_length=13, null=True)
    surname = models.CharField(max_length=100)
    ttaccom = models.CharField(max_length=2, null=True)
    ttpcode = models.CharField(max_length=8, null=True)

    class Meta:
        db_table = 'data_futures_student'

    def children(self) -> list[models.QuerySet]:
        return [self.disability_set.all(), self.engagement_set.all()]


class Disability(XMLStagingModel, models.Model):
    xml_fields = ['disability']

    # structure
    student = models.ForeignKey('Student', on_delete=models.CASCADE)

    # values
    disability = models.IntegerField()

    class Meta:
        db_table = 'data_futures_disability'


class Engagement(XMLStagingModel, models.Model):
    xml_fields = ['numhus', 'engexpectedenddate', 'engstartdate', 'feeelig', 'rcstdnt']

    # structure
    student = models.ForeignKey('Student', on_delete=models.CASCADE)

    # values
    numhus = models.CharField(max_length=50)
    engexpectedenddate = models.DateField()  # todo: nullable? or just end of the ac. year
    engstartdate = models.DateField()
    feeelig = models.CharField(max_length=2)
    # nhsemp  # todo: verify that none of our short-courses are PSRB-accredited
    rcstdnt = models.IntegerField(null=True)

    class Meta:
        db_table = 'data_futures_engagement'

    def children(self) -> list[models.QuerySet]:
        return [
            self.entryprofile_set.all(),
            self.leaver_set.all(),
            self.qualificationawarded_set.all(),
            self.studentcoursesession_set.all(),
        ]


class EntryProfile(XMLStagingModel, models.Model):
    xml_fields = ['careleaver', 'highestqoe', 'pared', 'permaddcountry', 'permaddpostcode']

    # structure
    engagement = models.ForeignKey('Engagement', on_delete=models.CASCADE)

    # values
    # todo: careleaver potentially empty by default, populated by business rules
    careleaver = models.CharField(max_length=2, null=True, default='99')
    highestqoe = models.CharField(max_length=5, null=True)  # nullable while qualification.entry_profile is
    pared = models.IntegerField(null=True)
    permaddcountry = models.CharField(max_length=2)  # domicile.  todo: Not Known value appears changed
    permaddpostcode = models.CharField(max_length=8, null=True)

    class Meta:
        db_table = 'data_futures_entry_profile'


class Leaver(XMLStagingModel, models.Model):
    xml_fields = ['engenddate', 'rsnengend']

    # structure
    engagement = models.ForeignKey('Engagement', on_delete=models.CASCADE)

    # values
    engenddate = models.DateField()
    rsnengend = models.CharField(max_length=2)

    class Meta:
        db_table = 'data_futures_leaver'


class QualificationAwarded(XMLStagingModel, models.Model):
    xml_fields = ['qualawardid', 'qualid', 'qualresult']

    # structure
    engagement = models.ForeignKey('Engagement', on_delete=models.CASCADE)

    # values
    qualawardid = models.CharField(max_length=50)  # unique per engagement
    qualid = models.CharField(max_length=50)  # fk to qualification
    qualresult = models.CharField(max_length=30, default='0013')  # award of credit

    class Meta:
        db_table = 'data_futures_qualification_awarded'


class StudentCourseSession(XMLStagingModel, models.Model):
    xml_fields = [
        'scsessionid',
        'courseid',
        'invoicefeeamount',
        'invoicehesaid',
        'rsnscsend',
        'scsenddate',
        'scsmode',
        'scsstartdate',
        'sessionyearid',
        'yearprg',
    ]

    # structure
    engagement = models.ForeignKey('Engagement', on_delete=models.CASCADE)

    # values
    scsessionid = models.CharField(max_length=50)  # unique per engagement
    courseid = models.CharField(max_length=50)  # fk to course
    invoicefeeamount = models.IntegerField(null=True)
    invoicehesaid = models.CharField(max_length=4, null=True, default='5050')  # Fees paid by student
    rsnscsend = models.CharField(max_length=2, null=True)
    scsenddate = models.DateField(null=True)
    scsmode = models.CharField(max_length=2, default='31')  # part-time
    scsstartdate = models.DateField()
    sessionyearid = models.CharField(max_length=50)  # fk to session year
    yearprg = models.IntegerField(default=99)  # concept doesn't apply

    class Meta:
        db_table = 'data_futures_student_course_session'

    def children(self) -> list[models.QuerySet]:
        return [
            self.fundingandmonitoring_set.all(),
            self.moduleinstance_set.all(),
            self.referenceperiodstudentload_set.all(),
            self.studylocation_set.all(),
        ]


class FundingAndMonitoring(XMLStagingModel, models.Model):
    xml_fields = ['elq', 'fundcomp', 'fundlength', 'nonregfee']

    # structure
    student_course_session = models.ForeignKey('StudentCourseSession', on_delete=models.CASCADE)

    # values
    elq = models.CharField(max_length=2, null=True)
    fundcomp = models.CharField(max_length=2, null=True)
    fundlength = models.CharField(max_length=2, default='02')  # standard length
    nonregfee = models.CharField(max_length=2, default='01')  # non-regulated fees

    class Meta:
        db_table = 'data_futures_funding_and_monitoring'


# todo: determine which (if any) students this should be returned for.
class FundingBody(XMLStagingModel, models.Model):
    # structure
    student_course_session = models.ForeignKey('StudentCourseSession', on_delete=models.CASCADE)

    # values
    fundingbody = models.CharField(max_length=4)

    class Meta:
        db_table = 'data_futures_funding_body'


class ModuleInstance(XMLStagingModel, models.Model):
    xml_fields = [
        'modinstid',
        'continuing',
        'mifeeamount',
        'modid',
        'modinstenddate',
        'modinststartdate',
        'moduleoutcome',
    ]

    # structure
    student_course_session = models.ForeignKey('StudentCourseSession', on_delete=models.CASCADE)

    # values
    modinstid = models.CharField(max_length=50)  # enrolment.id
    continuing = models.CharField(max_length=2, null=True)  # only required if we have modules spanning two SCSes
    mifeeamount = models.IntegerField(null=True)
    modid = models.CharField(max_length=50)  # fk to module
    modinstenddate = models.DateField(null=True)
    modinststartdate = models.DateField()
    moduleoutcome = models.CharField(max_length=2, null=True)

    class Meta:
        db_table = 'data_futures_module_instance'


class ReferencePeriodStudentLoad(XMLStagingModel, models.Model):
    xml_fields = ['refperiod', 'year', 'rpstuload']

    # structure
    student_course_session = models.ForeignKey('StudentCourseSession', on_delete=models.CASCADE)

    # values
    refperiod = models.CharField(max_length=2)
    year = models.IntegerField()
    rpstuload = models.DecimalField(max_digits=4, decimal_places=1)

    class Meta:
        db_table = 'data_futures_reference_period_student_load'


class StudyLocation(XMLStagingModel, models.Model):
    xml_fields = ['studylocid', 'distance', 'studyproportion', 'venueid']

    # structure
    student_course_session = models.ForeignKey('StudentCourseSession', on_delete=models.CASCADE)

    # values
    studylocid = models.CharField(max_length=50)  # unique across the SCS
    distance = models.CharField(max_length=2, null=True)
    studyproportion = models.IntegerField()
    venueid = models.CharField(max_length=50, null=True)  # fk to Venue, where not distance learning

    class Meta:
        db_table = 'data_futures_study_location'


class Venue(XMLStagingModel, models.Model):
    xml_fields = ['venueid', 'postcode', 'venuename', 'venueukprn']

    # structure
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE)

    # values
    venueid = models.CharField(max_length=50)
    postcode = models.CharField(max_length=8)
    venuename = models.CharField(max_length=255)
    venueukprn = models.CharField(max_length=8, default=INSTITUTION_CODE)

    class Meta:
        db_table = 'data_futures_venue'
