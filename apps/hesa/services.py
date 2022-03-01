import itertools
import re
from datetime import date
from typing import Iterable, Optional

from celery_progress.backend import ProgressRecorder
from lxml import etree

from django.conf import settings
from django.db.models import F, FilteredRelation, OuterRef, Prefetch, Q, Subquery

from apps.core.utils import strings
from apps.enrolment.models import Enrolment
from apps.finance.models import Accounts, Ledger
from apps.module.models import Module
from apps.programme.models import Programme
from apps.qualification_aim.models import QualificationAim
from apps.student.models import Student

from . import models
from .models.staging_tables import XMLStagingModel

EMPTY_ELEMENT = '<EMPTY>'

OVERSEAS_STUDY_LOCATION = 9
SSN_OTHER_ID = 9
UNKNOWN_DOMICILE = 181
PASS_RESULT = '1'
FAIL_RESULT = '2'
INCOMPLETE_RESULT = '4'
UNKNOWN_RESULT = '6'
COMPLETE_PENDING_RESULT = 'C'

FEE_TRANSACTION_TYPE = 1


# todo: determine if we need both the task and services
def create_return(
    academic_year, created_by, *, recorder: Optional[ProgressRecorder] = None, run_xml=False
) -> models.Batch:
    """The schedulable routine which call the magic below"""
    return HESAReturn(academic_year, created_by, recorder=recorder).create()


class HESAReturn:
    def __init__(self, academic_year: int, created_by: str, *, recorder: Optional[ProgressRecorder] = None) -> None:
        self.academic_year = academic_year
        self.batch = models.Batch.objects.create(academic_year=self.academic_year, created_by=created_by)
        self.recorder = recorder

        # Universal base query
        # could potentially use other Models, but it sits nicely as the m2m between QA and Module
        self.base_query = (
            Enrolment.objects.filter(
                module__start_date__gte=date(academic_year, 8, 1),  # This year
                module__start_date__lt=date(academic_year + 1, 7, 30),
                module__credit_points__gt=0,  # Exclude Cert HE dummy module, etc
                qa__programme__qualification__on_hesa_return=True,  # Valid programme
                status__on_hesa_return=True,  # Confirmed (etc) student
            )
            # Exclude students lacking both a domicile and gender (a shorthand for incomplete registrations)
            .exclude(Q(qa__student__domicile=UNKNOWN_DOMICILE) | Q(qa__student__gender__isnull=True))
            # We exclude distance learners
            .exclude(qa__study_location_id=OVERSEAS_STUDY_LOCATION)
            # and cancelled courses
            .exclude(module__is_cancelled=True)
        )

    def _set_progress(self, current: int, total: int, description: str = '') -> None:
        if self.recorder:
            self.recorder.set_progress(current=current, total=total, description=description)

    def create(self) -> models.Batch:
        """Populate the tables in order, updating the status after each"""
        steps = 11
        self._set_progress(1, steps, 'Institution')
        self._institution()
        self._set_progress(2, steps, 'Student')
        self._student()
        self._set_progress(3, steps, 'Courses')
        self._course()
        self._set_progress(4, steps, 'Course subjects')
        self._course_subject()
        self._set_progress(5, steps, 'Modules')
        self._module()
        self._set_progress(6, steps, 'Module subjects')
        self._module_subject()
        self._set_progress(7, steps, 'Instances')
        self._instance()
        self._set_progress(8, steps, 'Entry profiles')
        self._entry_profile()
        self._set_progress(9, steps, 'Students on modules')
        self._student_on_module()
        self._set_progress(10, steps, 'Post-processing business rules')
        self._post_processing()

        return self.batch

    def _institution(self):
        models.Institution.objects.create(
            batch=self.batch,
            recid=f'{self.academic_year % 100}051',
        )

    def _instance_id(self, qa_id: int) -> str:
        # Encode the academic year and QA id to make an instance id (unique each year)
        return f'{qa_id}-{self.academic_year}'

    def _student(self) -> None:
        in_query = self.base_query.values('qa__student__id')

        results = (
            Student.objects.filter(id__in=Subquery(in_query))
            .select_related('nationality')
            .annotate(
                default_address=FilteredRelation('address', condition=Q(address__is_default=True)),
                postcode=F('default_address__postcode'),
                ssn_row=FilteredRelation('other_id', condition=Q(other_id__id=SSN_OTHER_ID)),
                ssn=F('ssn_row__id'),
            )
            .order_by('id')
            .distinct()
        )

        for row in results:
            models.Student.objects.create(
                batch=self.batch,
                student=row.id,
                husid=str(row.husid).zfill(13),
                ownstu=row.sits_id or row.id,  # If a student's on SITS, we use that id, to allow amalgamation to work
                birthdte=row.birthdate,
                surname=row.surname.upper(),
                fnames=row.firstname.upper() + (' ' + row.middlename.upper() if row.middlename else ''),
                sexid=row.sex,
                sexort=row.sexual_orientation_id,
                genderid=row.gender_identity_id,
                nation=row.nationality.hesa_code,
                ethnic=str(row.ethnicity_id).zfill(2),
                disable=str(row.disability_id or 0).zfill(2),  # todo: remove 0 once fixture & default are in place
                ttaccom=row.termtime_accommodation,
                ttpcode=_correct_postcode(row.termtime_postcode or row.postcode or ''),
                ssn=row.ssn,
                relblf=str(row.religion_or_belief_id).zfill(2),
            )

    def _instance(self) -> None:
        in_query = self.base_query.values('qa__id')

        results = (
            QualificationAim.objects.filter(id__in=Subquery(in_query))
            .select_related(
                'programme__qualification',
                'entry_qualification',
                'study_location',
                'programme',
                'student',
            )
            .prefetch_related(
                # Get the year's enrolments, with related models, in order to calculate things like stuload
                Prefetch(
                    'enrolments',
                    to_attr='returned_enrolments',
                    queryset=Enrolment.objects.filter(id__in=self.base_query.values('id'))
                    .select_related('module', 'result')
                    .prefetch_related(
                        # And get each enrolment's fees, to calculate grossfee and netfee
                        # todo: consider annotating these instead, to simplify the logic
                        Prefetch(
                            'ledger_set',
                            to_attr='fee_ledger_items',
                            queryset=Ledger.objects.filter(type__id=FEE_TRANSACTION_TYPE, account=Accounts.DEBTOR),
                        ),
                    ),
                ),
            )
            .order_by('id')
            .distinct()
        )

        for row in results:
            enrolments: Iterable[Enrolment] = row.returned_enrolments  # type: ignore
            reason_for_ending = _reason_for_ending(enrolments=enrolments)
            models.Instance.objects.create(
                batch=self.batch,
                qa=row.id,
                instanceid=self._instance_id(row.id),
                ownstu_fk=row.student.sits_id or row.student.id,
                numhus=self._instance_id(row.id),
                courseid=row.programme.id,
                comdate=min(enrolment.module.start_date for enrolment in enrolments if enrolment.module.start_date),
                mode=row.programme.study_mode,
                stuload=sum(enrolment.module.full_time_equivalent for enrolment in enrolments),
                # our short courses don't really have an end date, so it's set to be the end of the academic year
                enddate=date(self.academic_year + 1, 7, 31),
                rsnend=reason_for_ending,
                # feeelig and fundcode get modified in post-processing
                feeelig=1 if row.student.is_eu else 2,
                fundcode=1 if row.student.is_eu else 2,
                mstufee='01',  # only varies on award courses
                fundlev=row.programme.funding_level,
                fundcomp=_completion(enrolments=enrolments),
                typeyr=row.programme.reporting_year_type,
                locsdy=row.study_location.hesa_code,
                disall=5 if row.student.disability_id != 0 else None,
                grossfee=_grossfee(enrolments=enrolments),
                netfee=_netfee(enrolments=enrolments),
                elq=_elq(qa=row),
                # Required field for our Master's level courses, but we have no research council students
                rcstdnt=99 if row.programme.qualification.hesa_code[0] in ('E', 'M') else None,
            )
            if reason_for_ending == '01':  # completed
                models.QualificationsAwarded.objects.create(
                    batch=self.batch,
                    instanceid_fk=self._instance_id(row.id),
                    qual=row.programme.qualification.hesa_code,
                )

    def _entry_profile(self) -> None:
        in_query = self.base_query.values('qa__id')

        results = (
            QualificationAim.objects.filter(id__in=Subquery(in_query))
            .annotate(
                default_address=FilteredRelation('student__address', condition=Q(student__address__is_default=True)),
                postcode=F('default_address__postcode'),
            )
            .select_related(
                'student__domicile',
                'student',
            )
            .order_by('id')
            .distinct()
        )

        for row in results:
            models.EntryProfile.objects.create(
                batch=self.batch,
                instanceid_fk=self._instance_id(row.id),
                domicile=row.student.domicile.hesa_code,
                qualent3=row.entry_qualification_id,
                postcode=_correct_postcode(row.student.termtime_postcode or row.postcode or '')
                if row.student.domicile.hesa_code in ('XF', 'XG', 'XH', 'XI', 'XK', 'XL', 'GG', 'JE', 'IM')
                else None,
                pared=row.student.parental_education_id,
            )

    def _module(self) -> None:
        in_query = self.base_query.values('module__id')

        results = Module.objects.filter(id__in=Subquery(in_query)).order_by('code').distinct()

        for row in results:
            models.Module.objects.create(
                batch=self.batch,
                module=row.id,
                modid=row.code,
                mtitle=strings.normalize_to_latin1(row.title),
                fte=row.full_time_equivalent,
                crdtpts=str(row.credit_points).zfill(3),
                levlpts=row.points_level_id,
            )

    def _student_on_module(self) -> None:
        results = self.base_query.select_related('module', 'result')

        for row in results:
            models.StudentOnModule.objects.create(
                batch=self.batch,
                enrolment=row.id,
                instanceid_fk=self._instance_id(row.qa_id),
                modid=row.module.code,
                modout=row.result.hesa_code,
            )

    def _module_subject(self) -> None:
        in_query = self.base_query.values('module__id')
        results = (
            models.ModuleHECoSSubject.objects.filter(module__in=Subquery(in_query))
            .select_related('hecos_subject', 'module')
            .order_by('module__code')
            .distinct()
        )

        for row in results:
            models.ModuleSubject.objects.create(
                batch=self.batch,
                modid_fk=row.module.code,
                modsbj=row.hecos_subject.id,
                modsbjp=row.percentage,
                costcn=row.hecos_subject.cost_centre_id,
            )

    def _course(self) -> None:
        in_query = self.base_query.values('qa__programme__id')

        results = (
            Programme.objects.filter(id__in=Subquery(in_query))
            .select_related('qualification')
            .order_by('id')
            .distinct()
        )

        for row in results:
            models.Course.objects.create(
                batch=self.batch,
                programme=row.id,
                courseid=row.id,
                owncourseid=row.id,
                courseaim=row.qualification.hesa_code,
                ctitle=row.title,
                msfund=str(row.funding_source or '').zfill(2),
            )

    def _course_subject(self):
        in_query = self.base_query.values('qa__programme__id')

        results = (
            models.ProgrammeHecosSubject.objects.filter(programme__in=Subquery(in_query))
            .select_related('hecos_subject')
            .order_by('programme')
            .distinct()
        )

        for row in results:
            models.CourseSubject.objects.create(
                batch=self.batch,
                courseid_fk=row.programme_id,
                sbjca=row.hecos_subject.id,
                sbjpcnt=row.percentage,
            )

    def _post_processing(self) -> None:
        """A series of tasks to shape the records to match HESA's XML expectations
        (mostly by removing data from fields where explicitly not required)

        Ensure every routine added here has a condition matching self.batch"""

        # Validation hacks while we have incomplete data:
        # todo: determine what to do with this.  Could just sit in the actual routines, if to be kept
        models.Instance.objects.filter(batch=self.batch, rsnend='00').update(rsnend='03')
        models.Instance.objects.filter(batch=self.batch, fundcomp=0).update(fundcomp=3)

        # Actual post-processing
        # todo: move into routines, or maybe .save()?

        # No ELQ where FEELIG is 2 or 3
        models.Instance.objects.filter(batch=self.batch, feeelig__in=(2, 3)).update(elq=None)

        # ELQ are not fundable
        models.Instance.objects.filter(batch=self.batch, elq__in=('01', '09'), fundcode=1,).update(
            fundcode=2  # Not fundable
        )

        # QR.C19051.Instance.FUNDCODE.8
        # FUNDCODE cannot be 1 where FUNDLEV = 20 (PGT) where QUALENT3 is Dphil/Masters

        # Subquery to find entry profiles with such QUALENT3s
        masters_and_dphil = (
            models.EntryProfile.objects.filter(
                batch=self.batch,
                qualent3__like='[MD]%',
            )
            .exclude(
                qualent3__in=('M44', 'M41', 'M71'),
            )
            .values('instanceid_fk')
        )

        # Query to update instances connected to those entry profiles
        models.Instance.objects.filter(
            batch=self.batch,
            fundlev=20,
            fundcode=1,
            instanceid__in=Subquery(masters_and_dphil),
        ).update(fundcode=2)

        # No Careleaver where Fundcode in 2, 3, 5 or Postgrad (M90, E90)
        instances = (
            models.Instance.objects.filter(
                batch=self.batch,
            )
            .annotate(
                # get the courseaim of the matching course in the same batch
                courseaim=Subquery(
                    models.Course.objects.filter(courseid=OuterRef('courseid'), batch=self.batch).values('courseaim')
                )
            )
            .filter(Q(fundcode__in=(2, 3, 5)) | Q(courseaim__in=('M90', 'E90')))
            .values('instanceid')
        )

        models.EntryProfile.objects.filter(batch=self.batch, instanceid_fk__in=Subquery(instances)).update(
            careleaver=None
        )

        # Pared only returned for fundable UG students
        instances = (
            models.Instance.objects.filter(batch=self.batch)
            .annotate(
                # get the courseaim of the matching course in the same batch
                courseaim=Subquery(
                    models.Course.objects.filter(courseid=OuterRef('courseid'), batch=self.batch).values('courseaim')
                )
            )
            .exclude(fundcode=1, courseaim__startswith='C')  # exclude fundable ug
            .values('instanceid')
        )

        models.EntryProfile.objects.filter(batch=self.batch, instanceid_fk__in=Subquery(instances)).update(pared=None)


def _correct_postcode(postcode: str) -> str:
    """Format UK postcodes while filtering out non-UK"""
    # UK govt regex from https://stackoverflow.com/questions/164979/regex-for-matching-uk-postcodes
    POSTCODE_REGEX = (
        r'^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})'
        r'|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})$'
    )
    postcode = postcode.replace(' ', '')
    if re.match(POSTCODE_REGEX, postcode):
        # Insert the space
        postcode = postcode[:-3] + ' ' + postcode[-3:]
        return postcode.upper()
    # Invalid or foreign postcode
    return EMPTY_ELEMENT


def _reason_for_ending(*, enrolments) -> str:
    results = {enrolment.result.hesa_code for enrolment in enrolments}
    if PASS_RESULT in results:
        return '01'  # completion
    if FAIL_RESULT in results:
        return '02'  # academic failure
    return '01'  # todo: reconsider fallback value


def _completion(*, enrolments) -> int:
    """Generates FUNDCOMP based on a set of enrolments"""
    result_set = {enrolment.result.hesa_code for enrolment in enrolments}
    if INCOMPLETE_RESULT in result_set:
        return 2  # did not complete
    if UNKNOWN_RESULT in result_set:
        return 3  # not yet complete
    if {PASS_RESULT, FAIL_RESULT, COMPLETE_PENDING_RESULT} & result_set:
        return 1  # complete
    return 0  # Invalid value # todo: reconsider how this operates


def _elq(*, qa: QualificationAim) -> str:
    if not qa.entry_qualification:
        return ''
    if qa.programme.qualification.elq_rank > qa.entry_qualification.elq_rank:
        return '03'
    return '01'


def _netfee(*, enrolments) -> int:
    def enrolment_sum(enrolment):
        return sum(line.amount for line in enrolment.fee_ledger_items)

    return round(sum(enrolment_sum(enrolment) for enrolment in enrolments))


def _grossfee(*, enrolments) -> int:
    def enrolment_sum(enrolment):
        return sum(line.amount for line in enrolment.fee_ledger_items if line.amount > 0)

    return round(sum(enrolment_sum(enrolment) for enrolment in enrolments))


def _model_to_node(model: XMLStagingModel) -> etree.Element:
    node = etree.Element(model.element_name)
    # Fill with elements
    for column in model.xml_fields:
        value = getattr(model, column)
        # hack to deal with qualification_awarded.class shadowing a reserved word
        if column == 'qual_class':
            column = 'class'
        if value is not None:
            # EMPTY_ELEMENT lets us handle conditionally-returned elements, e.g. postcode and ttpcode: they
            # must not exist for overseas, but can exist and be empty for UK
            etree.SubElement(node, column.upper()).text = str(value).replace(EMPTY_ELEMENT, '')
        elif column in model.xml_required:
            # Empty element for a null
            etree.SubElement(node, column.upper())

    # Create subnodes if any exist
    for child in itertools.chain.from_iterable(model.children()):
        node.append(_model_to_node(child))

    return node


def _generate_tree(batch: int) -> str:
    root = etree.Element('StudentRecord')
    institution = models.Institution.objects.get(batch=batch)
    root.append(_model_to_node(institution))

    return etree.tostring(root, pretty_print=True).decode('utf8')


def save_xml(batch: models.Batch) -> None:
    # create the media subfolder if required
    file_path = settings.PROTECTED_MEDIA_ROOT / 'hesa'
    file_path.mkdir(parents=True, exist_ok=True)

    filename = f'conted_batch_{batch.id}.xml'
    fullpath = file_path / filename
    with open(fullpath, 'w') as f:
        xml_string = _generate_tree(batch.id)
        f.write(xml_string)
    batch.filename = filename
    batch.save()
