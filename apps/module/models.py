from __future__ import annotations

from datetime import datetime
from typing import Optional

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.expressions import F
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.functional import cached_property

from apps.core.models import SignatureModel
from apps.core.utils.dates import academic_year
from apps.core.utils.models import UpperCaseCharField
from apps.fee.models import Accommodation
from redpot.settings import PUBLIC_WEBSITE_URL


class Statuses(models.IntegerChoices):
    UNPUBLISHED = 10
    NOT_YET_OPEN = 11
    CLOSED = 30
    OPEN = 20
    RUNNING_AND_OPEN = 21
    RUNNING_AND_CLOSED = 31
    ENDED = 32
    CANCELLED = 33
    FULL = 35


class ModuleManager(models.Manager):
    """A manager which defers html blob fields by default"""

    defer_fields = [
        'overview',
        'accommodation',
        'application',
        'assessment_methods',
        'certification',
        'course_aims',
        'level_and_demands',
        'libraries',
        'payment',
        'programme_details',
        'recommended_reading',
        'scholarships',
        'snippet',
        'teaching_methods',
        'teaching_outcomes',
        'selection_criteria',
        'it_requirements',
        'further_details',
    ]

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().defer(*self.defer_fields)


class Module(SignatureModel):
    code = UpperCaseCharField(
        max_length=12,
        help_text='For details on codes, see <link>',
        validators=[RegexValidator(r'^[A-Z]\d{2}[A-Z]\d{3}[A-Z]\w[A-Z]$', message='Must be in the form A12B345CDE')],
        unique=True,
    )
    title = models.CharField(max_length=80)
    url = models.SlugField(max_length=256, blank=True, null=True)

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    michaelmas_end = models.DateField(blank=True, null=True)
    hilary_start = models.DateField(blank=True, null=True)

    division = models.ForeignKey(
        'core.Division',
        models.DO_NOTHING,
        db_column='division',
        limit_choices_to=models.Q(id__gt=8) | models.Q(id__lt=5),
        default=1,
    )
    portfolio = models.ForeignKey('core.Portfolio', models.DO_NOTHING, db_column='portfolio', default=1)

    status = models.ForeignKey('ModuleStatus', models.DO_NOTHING, db_column='status', default=10)
    max_size = models.IntegerField(blank=True, null=True)

    image = models.ImageField(upload_to='uploads/%Y/%m/%d/', max_length=512, blank=True, null=True)

    # type = models.ForeignKey('ModuleType', models.DO_NOTHING, db_column='type', blank=True, null=True)  # noqa: E800

    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    publish_date = models.DateField(blank=True, null=True)
    open_date = models.DateField(blank=True, null=True)
    closed_date = models.DateTimeField(blank=True, null=True)
    unpublish_date = models.DateField(blank=True, null=True)

    single_places = models.IntegerField(blank=True, null=True)
    twin_places = models.IntegerField(blank=True, null=True)
    double_places = models.IntegerField(blank=True, null=True)
    location = models.ForeignKey('Location', models.DO_NOTHING, db_column='location', blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    meeting_time = models.CharField(max_length=32, blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)
    no_meetings = models.IntegerField(blank=True, null=True)

    auto_publish = models.BooleanField(default=False)

    is_published = models.BooleanField(default=False)
    # finance_code = models.CharField(max_length=64, blank=True, null=True)  # noqa: E800 # todo: should this be used?
    email = models.CharField(max_length=256, blank=True, null=True)
    phone = models.CharField(max_length=256, blank=True, null=True)

    source_module_code = models.CharField(max_length=12, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    accommodation = models.TextField(blank=True, null=True)
    how_to_apply = models.TextField(blank=True, null=True, db_column='application')
    assessment_methods = models.TextField(blank=True, null=True)
    certification = models.TextField(blank=True, null=True)
    course_aims = models.TextField(blank=True, null=True)
    level_and_demands = models.TextField(blank=True, null=True)
    libraries = models.TextField(blank=True, null=True)
    payment = models.TextField(blank=True, null=True)
    programme_details = models.TextField(blank=True, null=True)
    recommended_reading = models.TextField(blank=True, null=True)
    scholarships = models.TextField(blank=True, null=True)
    snippet = models.CharField(max_length=512, blank=True, null=True)
    teaching_methods = models.TextField(blank=True, null=True)
    teaching_outcomes = models.TextField(blank=True, null=True)
    selection_criteria = models.TextField(blank=True, null=True)
    it_requirements = models.TextField(blank=True, null=True)
    credit_points = models.IntegerField(blank=True, null=True)
    points_level = models.IntegerField(blank=True, null=True)
    enrol_online = models.BooleanField(blank=True, null=True)
    non_credit_bearing = models.BooleanField(default=True)
    auto_feedback = models.BooleanField(default=True)
    auto_reminder = models.BooleanField(default=True)
    no_search = models.BooleanField(default=False)
    week_number = models.IntegerField(blank=True, null=True)

    custom_fee = models.CharField(max_length=1012, blank=True, null=True)
    format = models.ForeignKey('ModuleFormat', models.DO_NOTHING, db_column='format', blank=True, null=True)

    is_cancelled = models.BooleanField(default=False)
    default_non_credit = models.BooleanField(blank=True, null=True)
    note = models.CharField(max_length=512, blank=True, null=True)
    terms_and_conditions = models.IntegerField(default=1)  # placeholder
    # terms_and_conditions = models.ForeignKey(    # noqa: E800
    #     'TermsAndConditions',                    # noqa: E800
    #     models.DO_NOTHING,                       # noqa: E800
    #     db_column='terms_and_conditions'         # noqa: E800
    # )                                            # noqa: E800
    apply_url = models.CharField(max_length=512, blank=True, null=True)
    further_details = models.TextField(blank=True, null=True)
    is_repeat = models.BooleanField(default=False)
    reminder_sent_on = models.DateTimeField(blank=True, null=True)
    room = models.CharField(max_length=12, blank=True, null=True)
    room_setup = models.CharField(max_length=12, blank=True, null=True)

    mailing_list = models.CharField(max_length=25, blank=True, null=True)
    notification = models.CharField(max_length=512, blank=True, null=True)
    cost_centre = models.CharField(max_length=6, blank=True, null=True)
    activity_code = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\d{2}$', message='Invalid code')],
        help_text='e.g. 00',
    )
    source_of_funds = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\w{5}$', message='Invalid code')],
        help_text='e.g. XA100',
    )
    fee_code = models.CharField(max_length=1, blank=True, null=True)

    half_term = models.DateField(blank=True, null=True)

    reading_list_url = models.TextField(blank=True, null=True)
    reading_list_links = models.BooleanField(blank=True, null=True)

    payment_plans = models.ManyToManyField(
        to='invoice.PaymentPlanType',
        through='invoice.ModulePaymentPlan',
    )
    hecos_subjects = models.ManyToManyField(to='hesa.HECoSSubject', through='hesa.ModuleHECoSSubject')
    subjects = models.ManyToManyField(
        to='Subject',
        through='ModuleSubject',
        verbose_name='Subjects (marketing)',
        help_text='These decide how the course is displayed in the website search results, and in print material',
    )
    marketing_types = models.ManyToManyField(
        to='MarketingType',
        through='ModuleMarketingType',
        help_text='These decide how the course is displayed in the website search results, and in print material',
    )
    objects = ModuleManager()

    class Meta:
        db_table = 'module'
        base_manager_name = 'objects'

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.url:
            self.url = slugify(self.title)
        # todo: setting is_cancelled, auto_publish on cancelled status.  Consider running update_status
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse('module:view', args=[self.id])

    def get_edit_url(self) -> str:
        return reverse('module:edit', args=[self.id])

    def get_website_url(self) -> str:
        return f'{PUBLIC_WEBSITE_URL}/courses/{self.url}?code={self.code}'

    @property
    def full_time_equivalent(self) -> float:
        """Calculate FTE, depending on level
        PG courses 100: FTE = 180 credit points
        UG courses 100: FTE = 120 credit points
        """

        # Todo: replace hard-coding, ensuring reliant routines do a select_related
        if self.points_level in [6, 7]:  # PG
            denominator = 180.0
        elif self.points_level in [1, 2]:  # UG
            denominator = 120.0
        else:
            return 0.0
        return round(100 * (self.credit_points or 0) / denominator)

    @property
    def long_form(self) -> str:
        if self.start_date:
            return f'{self.code} - {self.title} ({self.start_date:%d %b %Y})'
        return f'{self.code} - {self.title}'

    def places_taken(self) -> int:
        return self.enrolments.filter(status__takes_place=True).count()

    def is_full(self) -> bool:
        return bool(self.max_size and self.places_taken() >= self.max_size)

    def get_singles_left(self) -> int:
        """Return [allocated places] - [booked places]"""
        bookings = self.enrolments.filter(accommodation__type=Accommodation.Types.SINGLE).count()
        return (self.single_places or 0) - bookings

    def get_twins_left(self) -> int:
        """Return [allocated places] - [booked places]"""
        bookings = self.enrolments.filter(accommodation__type=Accommodation.Types.TWIN).count()
        return (self.twin_places or 0) - bookings

    @property
    def finance_code(self) -> Optional[str]:
        if self.cost_centre and self.activity_code and self.source_of_funds:
            return f'{self.cost_centre} {self.activity_code} {self.source_of_funds}'
        return None

    def other_runs(self):
        # Provides a list of other module runs, if url is set
        if self.url:
            return (
                Module.objects.filter(url=self.url, division=self.division)
                .exclude(id=self.id)
                .order_by(F('start_date').desc(nulls_last=True))
            )
        return Module.objects.none()

    def next_run(self) -> Optional[Module]:
        if self.start_date:
            return (
                self.other_runs()
                .filter(is_published=True, start_date__gte=self.start_date)
                .order_by('-start_date')
                .first()
            )
        return None

    @cached_property
    def _publish_check(self) -> dict:
        errors = {}

        if not self.snippet:
            errors['snippet'] = 'Snippet required'
        if not self.overview:
            errors['overview'] = 'Overview required'
        if not self.email:
            errors['email'] = 'Email required'
        if not self.programmes.exists():
            errors['programme'] = 'Not attached to a programme'
        if not self.marketing_types.exists():
            errors['marketing_type'] = 'Missing a marketing type'
        if not self.subjects.exists():
            errors['subject'] = 'Missing a marketing subject'
        if not self.custom_fee and not self.fees.filter(is_visible=True, type__is_tuition=True, eu_fee=False).exists():
            errors['fee'] = 'Published non-EU programme fee required'
        if not self.location_id:
            errors['location'] = 'Location required'
        if not self.format_id:
            errors['format'] = 'Format required'
        if self.enrol_online and not self.finance_code:
            errors['enrol_online'] = 'Finance code components required for online enrolment'
        # if self.proposal.status < 5:
        #     errors['proposal'] = 'Proposal unapproved' # Todo: Implement

        return {
            'success': not errors,
            'errors': errors,
        }

    @property
    def is_publishable(self) -> bool:
        return self._publish_check['success']

    @property
    def publish_errors(self) -> dict:
        return self._publish_check['errors']

    @cached_property
    def prospectus_check(self, prospectus_year: int = None) -> dict:
        """Checks if a module will be included in a year's prospectus (the upcoming academic year, by default)"""
        if not prospectus_year:
            prospectus_year = academic_year() + 1

        # We only include one academic year, hiding any cancelled or non-searchable courses
        in_scope = academic_year(self.start_date) == prospectus_year and not self.is_cancelled and not self.no_search

        errors = {}
        if in_scope:
            if not self.format_id:
                errors['format'] = 'Format required'
            if not self.snippet:
                errors['snippet'] = 'Snippet required'
            if (
                not self.custom_fee
                and not self.fees.filter(is_visible=True, type__is_tuition=True, eu_fee=False).exists()
            ):
                errors['fee'] = 'Published non-EU programme fee required'
            if not self.subjects.exists():
                errors['subject'] = 'Missing a marketing subject'

        return {'success': in_scope and not errors, 'errors': errors, 'year': prospectus_year, 'included': in_scope}

    def _get_auto_status(self):
        now = datetime.now()
        today = now.date()

        # Automatic date logic
        if self.publish_date > today or self.unpublish_date and today >= self.unpublish_date:
            # Todo: determine if the Unpublished status has any value
            return Statuses.UNPUBLISHED
        elif self.is_cancelled:
            return Statuses.CANCELLED
        elif self.open_date > today >= self.publish_date:
            return Statuses.NOT_YET_OPEN
        elif self.start_date > today and now >= self.closed_date:
            return Statuses.CLOSED
        elif self.start_date > today >= self.open_date:
            return Statuses.OPEN
        elif self.closed_date > now and today >= self.start_date:
            return Statuses.RUNNING_AND_OPEN
        elif self.end_date >= today and now >= self.closed_date:
            return Statuses.RUNNING_AND_CLOSED
        elif today > self.end_date:
            return Statuses.ENDED
        else:
            # Todo: determine if this has any value
            return Statuses.UNPUBLISHED  # All others are unpublished, if any others exist

    def update_status(self) -> dict:
        """Routine to update module status and is_published if set to automatic publication"""

        now = datetime.now()
        today = now.date()

        # Store initial values to check for changes
        initial_status = self.status_id
        initial_pub = self.is_published

        if self.auto_publish:
            # Automatic only, and we require start and end dates
            if self.publish_date and self.start_date and self.end_date:
                # Default dates (unpublish is not required, and so is set later)
                if not self.open_date:
                    self.open_date = self.publish_date
                if not self.closed_date:
                    # If undefined, default our closing to midnight the day the course starts
                    self.closed_date = datetime.combine(self.start_date, datetime.min.time())

                self.status_id = self._get_auto_status()

                # Full courses overrides current statuses
                if self.status_id in (Statuses.CLOSED, Statuses.OPEN, Statuses.RUNNING_AND_OPEN) and self.is_full():
                    self.status_id = Statuses.FULL

                self.is_published = (
                    (not self.unpublish_date or self.unpublish_date >= today)
                    # Status flagged as publishable
                    and self.status.publish
                    # Only do publishable check if not already publishable
                    and (self.is_published or self.is_publishable)
                )

                # Notify weeklyclasses if a course isn't published ONLY because of a proposal being incomplete
                # todo: determine usefulness of this check
                # if not self.is_published and idb.module_status(self.status_id).publish:  # noqa: E800
                #     _check_ongoing_proposal(self.id)  # noqa: E800
            else:
                # Lacks required fields for auto
                self.is_published = False

        else:
            # Manual. Unpublish if it fails the check
            self.is_published = self.is_published and self.is_publishable

        # Check for changes, and only update the db if found
        changed = initial_status != self.status_id or initial_pub != self.is_published
        if changed:
            self.save()

        return {
            'changed': changed,
            'old_status': initial_status,
            'new_status': self.status_id,
            'old_published': initial_pub,
            'new_published': self.is_published,
        }

    def clean(self) -> None:
        # Check both term start/end date fields are filled, or neither
        if bool(self.hilary_start) != bool(self.michaelmas_end):
            raise ValidationError(
                {
                    'hilary_start': 'You must provide both term dates',
                    'michaelmas_end': 'You must provide both term dates',
                }
            )

        # Check end_date is equal or later to start_date
        if self.end_date and not self.start_date:
            raise ValidationError(
                {
                    'start_date': 'Please set a start date',
                }
            )
        elif self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError(
                {
                    'end_date': 'End date cannot be earlier than start date',
                }
            )

        # Check if all components that make up the finance code are supplied, or none
        finance_components = [self.cost_centre, self.activity_code, self.source_of_funds]
        if any(finance_components) and not all(finance_components):
            raise ValidationError(
                {
                    'cost_centre': 'Please provide all of cost centre, activity code and source of funds, or none',
                }
            )

        if not all(finance_components) and self.enrol_online:
            raise ValidationError(
                {
                    'enrol_online': 'Online enrolment disallowed without cost centre, '
                    'activity code and source of funds',
                }
            )


class ModuleStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64)
    publish = models.BooleanField()
    short_desc = models.CharField(max_length=50, blank=True, null=True)
    waiting_list = models.BooleanField()

    class Meta:
        db_table = 'module_status'
        ordering = ['id']

    def __str__(self) -> str:
        return str(self.description)


class ModuleFormat(models.Model):
    description = models.CharField(max_length=50)

    class Meta:
        db_table = 'module_format'

    def __str__(self) -> str:
        return str(self.description)


class Location(SignatureModel):
    address = models.CharField(max_length=128)
    city = models.CharField(max_length=64, blank=True, null=True)
    postcode = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    building = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'location'

    def __str__(self) -> str:
        if self.city and self.building:
            return f'{self.building}, {self.city}'
        elif self.building:
            return self.building
        return 'Invalid: no city or building'


class Waitlist(models.Model):
    """A student's spot on a module waitlist"""

    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module', related_name='waitlists')
    student = models.ForeignKey('student.Student', models.DO_NOTHING, db_column='student', related_name='waitlists')
    listed_on = models.DateTimeField(default=datetime.now)
    emailed_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'module_waitlist'

    def get_absolute_url(self) -> str:
        return '#'

    def get_edit_url(self) -> str:
        return '#'

    def get_delete_url(self) -> str:
        return '#'


class Book(models.Model):
    module = models.ForeignKey('Module', models.DO_NOTHING, db_column='module', related_name='books')
    title = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=24)
    additional_information = models.TextField(blank=True, null=True)
    solo_link = models.TextField(blank=True, null=True)
    isbn_shelfmark = models.TextField(db_column='ISBN_shelfmark', blank=True, null=True)  # Field name made lowercase.
    price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    library_note = models.TextField(blank=True, null=True)
    status = models.ForeignKey('BookStatus', models.DO_NOTHING, db_column='status')

    class Meta:
        db_table = 'book'

    def get_absolute_url(self) -> str:
        return '#'

    def get_edit_url(self) -> str:
        return '#'

    def get_delete_url(self) -> str:
        return '#'


class BookStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    status = models.TextField()

    class Meta:
        db_table = 'book_status'

    def __str__(self) -> str:
        return str(self.status)


class Subject(models.Model):
    name = models.CharField(max_length=64)
    area = models.CharField(max_length=64)

    class Meta:
        db_table = 'subject'
        ordering = ('name',)

    def __str__(self) -> str:
        return str(self.name)

    def long_form(self) -> str:
        return f'{self.name} ({self.area})'


class ModuleSubject(models.Model):
    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module')
    subject = models.ForeignKey('Subject', models.DO_NOTHING, db_column='subject')

    class Meta:
        db_table = 'module_subject'
        unique_together = (('module', 'subject'),)


class MarketingType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        db_table = 'marketing_type'

    def __str__(self) -> str:
        return str(self.name)


class ModuleMarketingType(models.Model):
    marketing_type = models.ForeignKey(MarketingType, models.DO_NOTHING, db_column='marketing_type')
    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module')

    class Meta:
        db_table = 'module_marketing_type'
        unique_together = (('module', 'marketing_type'),)
