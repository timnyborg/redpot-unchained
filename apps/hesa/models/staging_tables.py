from __future__ import annotations

from datetime import datetime
from typing import Iterable

from django.db import models

INSTITUTION_CODE = 10007774


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
        db_table = 'hesa_batch'


class Course(XMLStagingModel, models.Model):
    parent_key = 'ukprn_fk'
    xml_fields = [
        'courseid',
        'owncourseid',
        'awardbod',
        'clsdcrs',
        'collorg',
        'courseaim',
        'ctitle',
        'msfund',
        'reducedc',
        'ttcid',
    ]

    batch = models.ForeignKey(Batch, models.DO_NOTHING, db_column='batch', blank=True, null=True)
    programme = models.IntegerField(blank=True, null=True)
    ukprn_fk = models.IntegerField(db_column='UKPRN_FK', default=INSTITUTION_CODE)
    courseid = models.CharField(db_column='COURSEID', max_length=8, blank=True, null=True)
    owncourseid = models.IntegerField(db_column='OWNCOURSEID', blank=True, null=True)
    reducedc = models.CharField(db_column='REDUCEDC', max_length=2, default='00')  # No reduced returns
    courseaim = models.CharField(db_column='COURSEAIM', max_length=3, blank=True, null=True)
    ctitle = models.CharField(db_column='CTITLE', max_length=128, blank=True, null=True)
    ttcid = models.IntegerField(
        db_column='TTCID', default=0
    )  # No teacher training courses?  May not be true for 1 or 2 PG
    collorg = models.CharField(
        db_column='COLLORG', max_length=4, default='0000'
    )  # No collab organizations?  May not be true for 1 or 2 PG
    clsdcrs = models.IntegerField(db_column='CLSDCRS', default=0)  # None are closed
    msfund = models.CharField(db_column='MSFUND', max_length=2, blank=True, null=True)
    awardbod = models.IntegerField(db_column='AWARDBOD', default=INSTITUTION_CODE)

    class Meta:
        db_table = 'hesa_course'
        unique_together = (('batch', 'courseid'),)

    def children(self) -> list[models.QuerySet]:
        return [CourseSubject.objects.filter(batch=self.batch, courseid_fk=self.courseid)]


class CourseSubject(XMLStagingModel, models.Model):
    xml_fields = ['sbjca', 'sbjpcnt']

    batch = models.ForeignKey(Batch, models.DO_NOTHING, db_column='batch')
    courseid_fk = models.CharField(db_column='COURSEID_FK', max_length=8, blank=True, null=True)
    sbjca = models.CharField(db_column='SBJCA', max_length=6, blank=True, null=True)
    sbjpcnt = models.IntegerField(db_column='SBJPCNT', blank=True, null=True)

    class Meta:
        db_table = 'hesa_course_subject'


class EntryProfile(XMLStagingModel, models.Model):
    xml_fields = ['careleaver', 'domicile', 'pared', 'postcode', 'qualent3']

    batch = models.ForeignKey(Batch, models.DO_NOTHING, db_column='batch')
    instanceid_fk = models.CharField(db_column='INSTANCEID_FK', max_length=16, blank=True, null=True)
    domicile = models.CharField(db_column='DOMICILE', max_length=2, blank=True, null=True)
    qualent3 = models.CharField(db_column='QUALENT3', max_length=3, blank=True, null=True)
    postcode = models.CharField(db_column='POSTCODE', max_length=32, blank=True, null=True)
    careleaver = models.IntegerField(db_column='CARELEAVER', blank=True, null=True, default=99)
    pared = models.IntegerField(db_column='PARED', blank=True, null=True, default=7)  # Not given

    class Meta:
        db_table = 'hesa_entry_profile'


class Instance(XMLStagingModel, models.Model):
    xml_fields = [
        'numhus',
        'courseid',
        'bridge',
        'campid',
        'comdate',
        'disall',
        'elq',
        'enddate',
        'exchange',
        'feeelig',
        'festumk',
        'fundcode',
        'fundcomp',
        'fundlev',
        'grossfee',
        'locsdy',
        'mcdate',
        'mode',
        'mstufee',
        'netfee',
        'rcstdnt',
        'reducedi',
        'rsnend',
        'specfee',
        'splength',
        'stuload',
        'typeyr',
        'unitlgth',
        'yearprg',
        'yearstu',
    ]
    xml_required = ['splength', 'mcdate', 'enddate']

    batch = models.ForeignKey(Batch, models.DO_NOTHING, db_column='batch')
    qa = models.IntegerField(blank=True, null=True)
    instanceid = models.CharField(db_column='INSTANCEID', max_length=16, blank=True, null=True)
    ownstu_fk = models.IntegerField(db_column='OWNSTU_FK', blank=True, null=True)
    numhus = models.CharField(db_column='NUMHUS', max_length=16, blank=True, null=True)
    reducedi = models.CharField(db_column='REDUCEDI', max_length=2, default='00')
    courseid = models.CharField(db_column='COURSEID', max_length=8)
    campid = models.CharField(db_column='CAMPID', max_length=1, default='A')  # We only have one campus
    comdate = models.DateField(db_column='COMDATE', blank=True, null=True)
    mode = models.IntegerField(db_column='MODE', blank=True, null=True)
    stuload = models.IntegerField(db_column='STULOAD', blank=True, null=True)
    splength = models.IntegerField(db_column='SPLENGTH', blank=True, null=True)
    unitlgth = models.IntegerField(db_column='UNITLGTH', default=9)  # Short courses don't use this
    enddate = models.DateField(db_column='ENDDATE', blank=True, null=True)
    rsnend = models.CharField(db_column='RSNEND', max_length=2, blank=True, null=True)
    feeelig = models.IntegerField(db_column='FEEELIG', blank=True, null=True)
    specfee = models.IntegerField(db_column='SPECFEE', default=9)
    mstufee = models.CharField(db_column='MSTUFEE', max_length=2, blank=True, null=True)
    fundlev = models.IntegerField(db_column='FUNDLEV', blank=True, null=True)
    fundcode = models.IntegerField(db_column='FUNDCODE', blank=True, null=True)
    yearstu = models.IntegerField(db_column='YEARSTU', default=1)  # New instances each year, per HESA's instruction
    yearprg = models.IntegerField(db_column='YEARPRG', default=99)
    fundcomp = models.IntegerField(db_column='FUNDCOMP', blank=True, null=True)
    typeyr = models.IntegerField(db_column='TYPEYR', blank=True, null=True)
    locsdy = models.CharField(db_column='LOCSDY', max_length=1, blank=True, null=True)
    exchange = models.CharField(db_column='EXCHANGE', max_length=1, default='N')  # Non-exchange
    disall = models.IntegerField(db_column='DISALL', blank=True, null=True)
    festumk = models.IntegerField(db_column='FESTUMK', default=2)
    grossfee = models.IntegerField(db_column='GROSSFEE', blank=True, null=True)
    netfee = models.IntegerField(db_column='NETFEE', blank=True, null=True)
    bridge = models.IntegerField(db_column='BRIDGE', default=0)  # No foundation courses
    elq = models.CharField(db_column='ELQ', max_length=2, blank=True, null=True)
    rcstdnt = models.IntegerField(db_column='RCSTDNT', blank=True, null=True)
    mcdate = models.DateField(db_column='MCDATE', blank=True, null=True)

    class Meta:
        db_table = 'hesa_instance'

    def children(self) -> list[models.QuerySet]:
        return [
            EntryProfile.objects.filter(batch=self.batch, instanceid_fk=self.instanceid),
            QualificationsAwarded.objects.filter(batch=self.batch, instanceid_fk=self.instanceid),
            StudentOnModule.objects.filter(batch=self.batch, instanceid_fk=self.instanceid),
        ]


class Institution(XMLStagingModel, models.Model):
    xml_fields = ['instapp', 'recid', 'ukprn']

    batch = models.ForeignKey(Batch, models.DO_NOTHING, db_column='batch')
    instapp = models.IntegerField(db_column='INSTAPP', default=0)
    recid = models.IntegerField(db_column='RECID')
    ukprn = models.IntegerField(db_column='UKPRN', default=INSTITUTION_CODE)

    class Meta:
        db_table = 'hesa_institution'

    def children(self) -> list[models.QuerySet]:
        return [
            Course.objects.filter(batch=self.batch),
            Module.objects.filter(batch=self.batch),
            Student.objects.filter(batch=self.batch),
        ]


class Module(XMLStagingModel, models.Model):
    xml_fields = ['modid', 'crdtpts', 'crdtscm', 'fte', 'levlpts', 'mtitle', 'pcolab', 'tinst']

    batch = models.ForeignKey(Batch, models.DO_NOTHING, db_column='batch')
    module = models.IntegerField(blank=True, null=True)
    ukprn_fk = models.IntegerField(db_column='UKPRN_FK', default=INSTITUTION_CODE)
    modid = models.CharField(db_column='MODID', max_length=32, blank=True, null=True)
    mtitle = models.CharField(db_column='MTITLE', max_length=80, blank=True, null=True)
    fte = models.DecimalField(db_column='FTE', max_digits=10, decimal_places=2, blank=True, null=True)
    pcolab = models.IntegerField(db_column='PCOLAB', default=0)
    crdtscm = models.IntegerField(db_column='CRDTSCM', default=1)
    crdtpts = models.CharField(db_column='CRDTPTS', max_length=3, blank=True, null=True)
    levlpts = models.IntegerField(db_column='LEVLPTS', blank=True, null=True)
    tinst = models.IntegerField(db_column='TINST', blank=True, null=True)

    class Meta:
        db_table = 'hesa_module'

    def children(self) -> list[models.QuerySet]:
        return [ModuleSubject.objects.filter(batch=self.batch, modid_fk=self.modid)]


class ModuleSubject(XMLStagingModel, models.Model):
    xml_fields = ['costcn', 'modsbj', 'modsbjp']

    batch = models.ForeignKey(Batch, models.DO_NOTHING, db_column='batch')
    modid_fk = models.CharField(db_column='MODID_FK', max_length=32)
    costcn = models.IntegerField(db_column='COSTCN', blank=True, null=True)
    modsbjp = models.IntegerField(db_column='MODSBJP')
    modsbj = models.CharField(db_column='MODSBJ', max_length=6)

    class Meta:
        db_table = 'hesa_module_subject'


class QualificationsAwarded(XMLStagingModel, models.Model):
    xml_fields = ['qual']

    batch = models.ForeignKey(Batch, models.DO_NOTHING, db_column='batch')
    instanceid_fk = models.CharField(db_column='INSTANCEID_FK', max_length=16, blank=True, null=True)
    qual = models.CharField(db_column='QUAL', max_length=3, blank=True, null=True)

    class Meta:
        db_table = 'hesa_qualifications_awarded'


class Student(XMLStagingModel, models.Model):
    xml_fields = [
        'husid',
        'ownstu',
        'birthdte',
        'disable',
        'ethnic',
        'fnames',
        'genderid',
        'nation',
        'relblf',
        'scn',
        'sexid',
        'sexort',
        'ssn',
        'surname',
        'ttaccom',
        'ttpcode',
    ]
    xml_required = ['BIRTHDTE', 'SCN', 'TTPCODE']

    batch = models.ForeignKey(Batch, models.DO_NOTHING, db_column='batch')
    student = models.IntegerField()
    ukprn_fk = models.IntegerField(db_column='UKPRN_FK', default=INSTITUTION_CODE)
    husid = models.CharField(db_column='HUSID', max_length=32, blank=True, null=True)
    ownstu = models.IntegerField(db_column='OWNSTU', blank=True, null=True)
    birthdte = models.DateField(db_column='BIRTHDTE', blank=True, null=True)
    surname = models.CharField(db_column='SURNAME', max_length=64, blank=True, null=True)
    fnames = models.CharField(db_column='FNAMES', max_length=64, blank=True, null=True)
    genderid = models.CharField(db_column='GENDERID', max_length=2, blank=True, null=True)
    sexid = models.IntegerField(db_column='SEXID', blank=True, null=True)
    sexort = models.CharField(db_column='SEXORT', max_length=2, blank=True, null=True)
    nation = models.CharField(db_column='NATION', max_length=2, blank=True, null=True)
    ethnic = models.IntegerField(db_column='ETHNIC', blank=True, null=True)
    disable = models.CharField(db_column='DISABLE', max_length=2, blank=True, null=True)
    ttaccom = models.IntegerField(db_column='TTACCOM', blank=True, null=True)
    ttpcode = models.CharField(db_column='TTPCODE', max_length=32, blank=True, null=True)
    ssn = models.CharField(db_column='SSN', max_length=32, blank=True, null=True)
    scn = models.IntegerField(db_column='SCN', blank=True, null=True)
    relblf = models.CharField(db_column='RELBLF', max_length=2, blank=True, null=True)

    class Meta:
        db_table = 'hesa_student'

    def children(self) -> list[models.QuerySet]:
        return [Instance.objects.filter(batch=self.batch, ownstu_fk=self.ownstu)]


class StudentOnModule(XMLStagingModel, models.Model):
    xml_fields = ['modid', 'modout', 'modstat']

    batch = models.ForeignKey(Batch, models.DO_NOTHING, db_column='batch')
    enrolment = models.IntegerField(blank=True, null=True)
    instanceid_fk = models.CharField(db_column='INSTANCEID_FK', max_length=16, blank=True, null=True)
    modid = models.CharField(db_column='MODID', max_length=16, blank=True, null=True)
    modstat = models.IntegerField(db_column='MODSTAT', default=2)  # Module contained within academic year
    modout = models.CharField(db_column='MODOUT', max_length=3, blank=True, null=True)

    class Meta:
        db_table = 'hesa_student_on_module'
