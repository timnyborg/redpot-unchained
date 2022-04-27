import itertools
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Optional

from celery_progress.backend import ProgressRecorder
from lxml import etree

from django.conf import settings
from django.db.models import F, FilteredRelation, Prefetch, Q, Subquery, TextChoices

from apps.core.utils import strings
from apps.enrolment.models import Enrolment
from apps.finance.models import Ledger
from apps.hesa.models import ModuleHECoSSubject
from apps.hesa.models.staging_tables import XMLStagingModel
from apps.module.models import Module
from apps.programme.models import Programme
from apps.qualification_aim.models import QualificationAim
from apps.student.models import Student

from . import models

OVERSEAS_STUDY_LOCATION = 9
SSN_OTHER_ID = 9
UNKNOWN_DOMICILE = 181
FEE_TRANSACTION_TYPE = 1


class ELQValues(TextChoices):
    """https://codingmanual.hesa.ac.uk/22056/FundingAndMonitoring/field/ELQ"""

    ELQ = '01'
    NOT_ELQ = '03'


class FundingCompletionValues(TextChoices):
    """https://codingmanual.hesa.ac.uk/22056/FundingAndMonitoring/field/ELQ"""

    COMPLETED = '01'
    DID_NOT_COMPLETE = '02'
    NOT_YET_COMPLETE = '03'


class EngagementEndReasons(TextChoices):
    """https://codingmanual.hesa.ac.uk/22056/Leaver/field/RSNENGEND"""

    AWARDED_CREDIT = "01"
    DEATH = "05"
    NO_CREDIT = "11"
    CREDIT_NOT_YET_KNOWN = "98"


class ModuleResults(TextChoices):
    """https://codingmanual.hesa.ac.uk/22056/ModuleInstance/field/MODULERESULT"""

    PASSED = "01"
    FAILED = "06"


class ModuleOutcomes(TextChoices):
    """https://codingmanual.hesa.ac.uk/22056/ModuleInstance/field/MODULEOUTCOME"""

    COMPLETE = "01"
    DID_NOT_COMPLETE = "03"
    NOT_FOR_CREDIT = "04"
    NOT_YET_KNOWN = "05"
    NOT_CODED = "96"


class Sexes(TextChoices):
    """https://codingmanual.hesa.ac.uk/22056/Student/field/SEXID"""

    FEMALE = "10"
    MALE = "11"
    OTHER = "12"


class DistanceValues(TextChoices):
    """https://codingmanual.hesa.ac.uk/22056/StudyLocation/field/DISTANCE"""

    IN_UK = "01"
    OUTSIDE_THE_UK = "02"  # likely never to be needed


@dataclass
class ReferencePeriod:
    """https://codingmanual.hesa.ac.uk/22056/ReferencePeriodStudentLoad/field/REFPERIOD"""

    code: str
    start_date: date
    end_date: date

    @classmethod
    def from_academic_year(cls, academic_year: int) -> list['ReferencePeriod']:
        return [
            cls("01", date(academic_year, 8, 1), date(academic_year, 11, 15)),
            cls("02", date(academic_year, 11, 16), date(academic_year + 1, 3, 15)),
            cls("03", date(academic_year + 1, 3, 16), date(academic_year + 1, 7, 31)),
        ]


def get_fte_in_reference_period(*, fte: float, start_date: date, end_date: date, ref_period: ReferencePeriod) -> float:
    """Calculate what proportion of the FTE is within a reference period's date range"""
    module_duration = (end_date - start_date).days + 1
    overlap = min(ref_period.end_date - start_date, end_date - ref_period.start_date).days + 1
    return max((overlap / module_duration) * fte, 0)


gender_to_sexid_map = {
    'M': Sexes.MALE,
    'F': Sexes.FEMALE,
    'I': Sexes.OTHER,
}


# todo: determine if we need both the task and services
def create_return(academic_year, created_by, *, recorder: Optional[ProgressRecorder] = None) -> models.Batch:
    """The schedulable routine which call the magic below"""
    return HESAReturn(academic_year, created_by, recorder=recorder).create()


class HESAReturn:
    def __init__(self, academic_year: int, created_by: str, *, recorder: Optional[ProgressRecorder] = None) -> None:
        self.academic_year = academic_year
        self.batch = models.Batch.objects.create(academic_year=self.academic_year, created_by=created_by)
        self.recorder = recorder

        # Universal base query
        # could potentially use other Models, but it sits nicely as the m2m between QA and Module
        self.start_date = date(academic_year, 8, 1)
        self.end_date = date(academic_year + 1, 7, 30)
        self.reference_periods = ReferencePeriod.from_academic_year(self.academic_year)

        self.base_query = (
            Enrolment.objects.filter(
                module__start_date__gte=self.start_date,  # This year
                module__start_date__lt=self.end_date,
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

    def set_progress(self, current: int, total: int, description: str = '') -> None:
        """Increment the state of the progress recorder, if present"""
        if self.recorder:
            self.recorder.set_progress(current=current, total=total, description=description)

    def create(self) -> models.Batch:
        """Populate all entity tables for the entire batch"""
        self.set_progress(1, 2, 'Courses, modules, etc.')
        self.build_courses()
        self.build_modules()
        self.build_session_year()
        self.build_venue()
        self.build_students()

        return self.batch

    def get_numhus(self, qa_id: int) -> str:
        # Encode the academic year and QA id to make an instance id (unique each year)
        return f'{qa_id}-{self.academic_year}'

    def build_students(self) -> None:
        """Generates all student entities, and their child entities"""
        in_query = self.base_query.values('qa__student__id')

        results = (
            Student.objects.filter(id__in=Subquery(in_query))
            .select_related(
                'nationality',
                'domicile',
                'ethnicity',
                'religion_or_belief',
                'sexual_orientation',
                'parental_education',
            )
            .annotate(
                default_address=FilteredRelation('address', condition=Q(address__is_default=True)),
                postcode=F('default_address__postcode'),
                ssn_row=FilteredRelation('other_id', condition=Q(other_id__id=SSN_OTHER_ID)),
                ssn=F('ssn_row__id'),
            )
            .order_by('id')
            .distinct()
        )

        for idx, row in enumerate(results):
            self.set_progress(idx, len(results), 'Students')
            hesa_student = self.batch.student_set.create(
                sid=str(row.husid).zfill(13),
                birthdte=row.birthdate,
                ethnic=row.ethnicity.data_futures_code,
                fnames=f"{row.firstname} {row.middlename or ''}".upper().strip(),
                genderid=str(row.gender_identity_id).zfill(2),
                nation=row.nationality.hesa_code.replace('ZZ', '97'),  # todo: swap this value post-legacy hesa
                ownstu=row.sits_id or row.id,
                religion=row.religion_or_belief.data_futures_code,
                sexid=gender_to_sexid_map.get(row.gender),
                sexort=row.sexual_orientation.data_futures_code,
                ssn=row.ssn,
                surname=row.surname.upper().strip(),
                ttaccom=str(row.termtime_accommodation).zfill(2) if row.termtime_accommodation else None,
                ttpcode=correct_postcode(row.termtime_postcode or row.postcode),
            )
            self.build_student_engagements(student=row, parent=hesa_student)

    def build_student_engagements(self, *, student: Student, parent: models.Student) -> None:
        """Generates the engagements for a single student"""
        in_query = self.base_query.values('qa__id')

        results = (
            student.qualification_aims.filter(id__in=Subquery(in_query))
            .select_related(
                'programme__qualification',
                'entry_qualification',
                'study_location',
                'programme',
                'student',
                'student__parental_education',
            )
            # The nested prefetches are just to improve performance by avoiding n+1s
            .prefetch_related(
                # Get the year's enrolments, with related models
                Prefetch(
                    'enrolments',
                    to_attr='returned_enrolments',
                    queryset=Enrolment.objects.filter(id__in=self.base_query.values('id'))
                    .select_related('module', 'result', 'module__points_level')  # level points used in fte calcs
                    .prefetch_related(
                        # And get each enrolment's fees
                        # todo: consider annotating these instead, to simplify the logic
                        Prefetch(
                            'ledger_set',
                            to_attr='fee_ledger_items',
                            queryset=Ledger.objects.filter(type__id=FEE_TRANSACTION_TYPE).debts(),
                        ),
                    ),
                ),
            )
            .order_by('id')
            .distinct()
        )

        for row in results:
            numhus = self.get_numhus(row.id)
            enrolments: Iterable[Enrolment] = row.returned_enrolments  # type: ignore
            reason_for_ending = get_reason_for_ending(enrolments=enrolments)
            engagement = parent.engagement_set.create(
                numhus=numhus,
                engexpectedenddate=self.end_date,
                engstartdate=min(enrolment.module.start_date for enrolment in enrolments),
                feeelig='01' if student.is_eu else '02',  # todo: changing to use a home_fees_eligible column
                # Required field for our Master's level courses, but we have no research council students
                rcstdnt='9997' if row.programme.qualification.data_futures_code[0] in ('E', 'M') else None,
            )

            engagement.entryprofile_set.create(
                careleaver='99' if row.programme.qualification.data_futures_code.startswith('C') else None,
                highestqoe=row.entry_qualification and row.entry_qualification.data_futures_code,
                pared=student.parental_education.data_futures_code
                if row.programme.qualification.data_futures_code.startswith('C')
                else None,
                # todo: swap this value post-legacy hesa
                permaddcountry=student.domicile.hesa_code.replace('ZZ', '97'),
                permaddpostcode=correct_postcode(student.postcode) if student.domicile.in_uk else None,
            )
            engagement.leaver_set.create(
                engenddate=self.end_date,
                rsnengend=reason_for_ending,
            )
            if reason_for_ending == EngagementEndReasons.AWARDED_CREDIT:
                engagement.qualificationawarded_set.create(
                    qualawardid=f'qual-award-{numhus}',
                    qualid=get_qualid(row.programme),
                )

            # Student course session and its children
            student_course_session = engagement.studentcoursesession_set.create(
                scsessionid=f'scs-{numhus}',
                courseid=row.programme.id,
                invoicefeeamount=get_netfee(enrolments=enrolments),
                rsnscsend='04',  # session ended
                scsenddate=self.end_date,
                scsstartdate=self.start_date,
                sessionyearid='short-course-year',
            )

            student_course_session.fundingandmonitoring_set.create(
                elq=get_elq(qa=row),
                fundcomp=get_funding_completion(enrolments=enrolments),
            )

            for reference_period in self.reference_periods:
                student_load = 0
                for enrolment in enrolments:
                    # Tally up the FTE of all the enrolments
                    student_load += get_fte_in_reference_period(
                        fte=enrolment.module.full_time_equivalent,
                        start_date=enrolment.module.start_date,
                        end_date=enrolment.module.end_date,
                        ref_period=reference_period,
                    )
                if student_load:
                    student_course_session.referenceperiodstudentload_set.create(
                        refperiod=reference_period.code,
                        year=self.academic_year,
                        rpstuload=student_load,
                    )

            # Todo: Currently assuming a single venue (Rewley), with 100% proportion.
            #  If it's determined that we need multiple venues, attached to modules or programmes,
            #  we'll need a routine to loop through the enrolments, and figure the proportion of the total for each
            #  venue.  It'd be fairly easy if it were a many-to-one relationship with programmes.
            distance_learning = row.study_location_id == OVERSEAS_STUDY_LOCATION
            student_course_session.studylocation_set.create(
                studylocid=f'study-location-{numhus}',
                distance=DistanceValues.IN_UK if distance_learning else None,
                studyproportion=100,
                venueid=None if distance_learning else 'rewley-house',
            )

            for enrolment in enrolments:
                student_course_session.moduleinstance_set.create(
                    modinstid=enrolment.id,
                    mifeeamount=sum(line.amount for line in enrolment.fee_ledger_items if line.amount > 0),
                    modid=enrolment.module.code,
                    modinstenddate=enrolment.module.start_date,
                    modinststartdate=enrolment.module.end_date,
                    moduleoutcome=enrolment.result.data_futures_outcome,
                )

    def build_modules(self) -> None:
        """Generates all module entities, and their child entities"""
        in_query = self.base_query.values('module__id')

        results = (
            Module.objects.filter(id__in=Subquery(in_query))
            .order_by('code')
            .select_related('points_level')
            .prefetch_related(
                # todo: check this is preventing n+1
                Prefetch('module_hecos_subjects', queryset=ModuleHECoSSubject.objects.select_related('hecos_subject'))
            )
            .distinct()
        )

        for row in results:
            module = self.batch.module_set.create(
                modid=row.code,
                crdtpts=str(row.credit_points).zfill(3),
                fte=row.full_time_equivalent,
                levlpts=row.points_level and row.points_level.data_futures_code,
                mtitle=strings.normalize_to_latin1(row.title),
            )
            # while we still derive cost centre from subject, we need to sum up percents if cost centres are the same
            cost_centres: defaultdict[int, int] = defaultdict(lambda: 0)
            for module_subject in row.module_hecos_subjects.all():
                module.modulesubject_set.create(
                    modsbj=module_subject.hecos_subject_id,
                    modproportion=module_subject.percentage,
                )
                cost_centres[module_subject.hecos_subject.cost_centre_id] += module_subject.percentage
            for cost_centre, percentage in cost_centres.items():
                module.modulecostcentre_set.create(
                    costcn=cost_centre,
                    costcnproportion=percentage,
                )

    def build_courses(self) -> None:
        """Generates all course entities, and their child entities"""

        in_query = self.base_query.values('qa__programme__id')

        results = (
            Programme.objects.filter(id__in=Subquery(in_query))
            .select_related('qualification')
            .prefetch_related('hecos_subjects')
            .order_by('id')
            .distinct()
        )

        for row in results:
            # Create a qualification for the programme
            qualid = get_qualid(row)
            qualification = self.batch.qualification_set.create(
                qualid=qualid,
                qualcat=row.qualification.data_futures_code,
            )
            # Child records for the qualification
            qualification.awardingbodyrole_set.create()
            for subject in row.programmehecossubject_set.all():
                qualification.qualificationsubject_set.create(
                    qualsubject=subject.hecos_subject_id,
                    qualproportion=subject.percentage,
                )
            # And the course itself
            course = self.batch.course_set.create(
                courseid=row.id,
                coursetitle=row.title,
                prerequisite='02' if row.qualification.is_postgraduate else '01',
                qualid=qualid,
            )
            course.courserole_set.create()

    def build_session_year(self):
        """Generates a standardized SessionYear entity"""

        self.batch.sessionyear_set.create(
            sessionyearid='short-course-year',
            systartdate=self.start_date,
            syenddate=self.end_date,
        )

    def build_venue(self):
        """Generates a standardized Venue entity"""

        self.batch.venue_set.create(
            venueid='rewley-house',
            postcode='OX1 2JA',
            venuename='Department for Continuing Education, Rewley House',
            venueukprn=models.INSTITUTION_CODE,
        )


def get_qualid(programme: Programme) -> str:
    """Generate a reusable QUALID"""
    return f'qual-{programme.id}'


def correct_postcode(postcode: Optional[str]) -> Optional[str]:
    """Format UK postcodes while filtering out non-UK"""
    if not postcode:
        return None
    # UK govt regex from https://stackoverflow.com/questions/164979/regex-for-matching-uk-postcodes
    postcode_regex = (
        r'^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})'
        r'|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})$'
    )
    postcode = postcode.replace(' ', '')
    if re.match(postcode_regex, postcode):
        # Insert the space
        postcode = postcode[:-3] + ' ' + postcode[-3:]
        return postcode.upper()
    # Invalid or foreign postcode
    return None


def get_reason_for_ending(*, enrolments) -> str:
    """Generate RSNENGEND from a set of enrolments"""
    points_awarded = sum(enrolment.points_awarded or 0 for enrolment in enrolments)
    results = {enrolment.result_id for enrolment in enrolments}
    if points_awarded:
        return EngagementEndReasons.AWARDED_CREDIT
    if ModuleOutcomes.NOT_YET_KNOWN in results:
        return EngagementEndReasons.CREDIT_NOT_YET_KNOWN
    return EngagementEndReasons.NO_CREDIT


def get_funding_completion(*, enrolments) -> str:
    """Generates FUNDCOMP based on a set of enrolments.
    todo: verify what the rules are re. modular short courses, ideally with the OFS
    """
    outcome_set = {enrolment.result.data_futures_outcome for enrolment in enrolments}
    if ModuleOutcomes.DID_NOT_COMPLETE in outcome_set:
        return FundingCompletionValues.DID_NOT_COMPLETE
    if ModuleOutcomes.NOT_YET_KNOWN in outcome_set:
        return FundingCompletionValues.NOT_YET_COMPLETE
    if ModuleOutcomes.COMPLETE in outcome_set:
        return FundingCompletionValues.COMPLETED
    return FundingCompletionValues.NOT_YET_COMPLETE  # Fallback value, usually indicating results not entered


def get_elq(*, qa: QualificationAim) -> str:
    if not qa.entry_qualification:
        return ''
    if qa.programme.qualification.elq_rank > qa.entry_qualification.elq_rank:
        return ELQValues.NOT_ELQ
    return ELQValues.ELQ


def get_netfee(*, enrolments) -> int:
    def enrolment_sum(enrolment):
        return sum(line.amount for line in enrolment.fee_ledger_items)

    return round(sum(enrolment_sum(enrolment) for enrolment in enrolments))


def _model_to_node(model: XMLStagingModel) -> etree.Element:
    """Convert an XMLStagingModel and its children into an xml tree"""
    node = etree.Element(model.element_name)
    # Fill with elements
    for column in model.xml_fields:
        value = getattr(model, column)
        if value is not None:
            etree.SubElement(node, column.upper()).text = str(value)

    # Create subnodes if any exist
    for child in itertools.chain.from_iterable(model.children()):
        node.append(_model_to_node(child))

    return node


def _generate_tree(batch: models.Batch) -> str:
    root = etree.Element('DataFutures')
    for child in itertools.chain.from_iterable(batch.children()):
        root.append(_model_to_node(child))

    return etree.tostring(root, pretty_print=True).decode('utf8')


def save_xml(batch: models.Batch) -> None:
    # create the media subfolder if required
    file_path = settings.PROTECTED_MEDIA_ROOT / 'hesa_data_futures'
    file_path.mkdir(parents=True, exist_ok=True)

    filename = f'conted_data_futures_batch_{batch.id}.xml'
    fullpath = file_path / filename
    with open(fullpath, 'w') as f:
        xml_string = _generate_tree(batch)
        f.write(xml_string)
    batch.filename = filename
    batch.save()
