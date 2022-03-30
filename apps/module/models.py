from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFit

from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.expressions import F
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.functional import cached_property

from apps.booking.models import Accommodation
from apps.core.models import SignatureModel
from apps.core.utils.dates import academic_year
from apps.core.utils.models import PhoneField, UpperCaseCharField
from redpot import storage_backends


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


class RoomSetups(models.TextChoices):
    SEMINR = 'SEMINR', 'Seminar'
    ECTR = 'ECTR', 'Computer teaching'
    BOARD = 'BOARD', 'Boardroom'
    CLASS = 'CLASS', 'Classroom'
    LECT = 'LECT', 'Lecture'
    UCHRS = 'UCHRS', 'U of chairs'
    UTBLS = 'UTBLS', 'U of tables'


class ModuleManager(models.Manager):
    """A manager which defers html blob fields by default"""

    defer_fields = [
        'overview',
        'accommodation',
        'how_to_apply',
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


# Common length limits for website text fields
MAX_WEBFIELD_LENGTH = 10000
webfield_attrs = {'validators': [validators.MaxLengthValidator(MAX_WEBFIELD_LENGTH)]}


def image_filename(instance: Module, filename: str) -> str:
    """Generates filenames for uploaded images including the module code"""
    today = date.today()
    return f'images/modules/{today.year}/{today.month:02}/{instance.code}_{filename}'


class Module(SignatureModel):
    code = UpperCaseCharField(
        max_length=12,
        validators=[RegexValidator(r'^[A-Z]\d{2}[A-Z]\d{3}[A-Z]\w[A-Z]$', message='Must be in the form A12B345CDE')],
        unique=True,
    )
    title = models.CharField(max_length=80)
    url = models.SlugField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name='URL',
        help_text='Leave empty to automatically generate from the title',
    )

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

    image = ProcessedImageField(
        storage=storage_backends.WebsiteStorage(),
        upload_to=image_filename,
        blank=True,
        null=True,
        processors=[ResizeToFit(1600, 1600)],
        format='JPEG',
        options={'quality': 70},
    )

    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    publish_date = models.DateField(blank=True, null=True)
    open_date = models.DateField(blank=True, null=True)
    closed_date = models.DateTimeField(blank=True, null=True)
    unpublish_date = models.DateField(blank=True, null=True)

    single_places = models.IntegerField(blank=True, null=True, verbose_name='Single rooms')
    twin_places = models.IntegerField(blank=True, null=True, verbose_name='Twin rooms')
    location = models.ForeignKey('Location', models.DO_NOTHING, db_column='location', blank=True, null=True)
    room = models.ForeignKey('Room', models.PROTECT, db_column='room', blank=True, null=True)
    room_setup = models.CharField(max_length=12, choices=RoomSetups.choices, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    meeting_time = models.CharField(
        max_length=32, blank=True, null=True, help_text='Optional. It is better to provide start and end times'
    )
    duration = models.FloatField(blank=True, null=True)
    no_meetings = models.IntegerField(blank=True, null=True)

    auto_publish = models.BooleanField(default=False)

    is_published = models.BooleanField(default=False)
    email = models.EmailField(max_length=256, blank=True, null=True)
    phone = PhoneField(max_length=256, blank=True, null=True)

    source_module_code = models.CharField(max_length=12, blank=True, null=True)
    overview = models.TextField(blank=True, null=True, **webfield_attrs)
    accommodation = models.TextField(blank=True, null=True, **webfield_attrs)
    how_to_apply = models.TextField(blank=True, null=True, db_column='application', **webfield_attrs)
    assessment_methods = models.TextField(blank=True, null=True, **webfield_attrs)
    certification = models.TextField(blank=True, null=True, **webfield_attrs)
    course_aims = models.TextField(blank=True, null=True, **webfield_attrs)
    level_and_demands = models.TextField(blank=True, null=True, **webfield_attrs)
    libraries = models.TextField(blank=True, null=True, **webfield_attrs)
    payment = models.TextField(blank=True, null=True, **webfield_attrs)
    programme_details = models.TextField(blank=True, null=True, **webfield_attrs)
    recommended_reading = models.TextField(blank=True, null=True, **webfield_attrs)
    scholarships = models.TextField(blank=True, null=True, verbose_name='Funding', **webfield_attrs)
    snippet = models.CharField(
        max_length=255, blank=True, null=True, help_text='Used in cards and search results. Maximum 255 characters'
    )
    teaching_methods = models.TextField(blank=True, null=True, **webfield_attrs)
    teaching_outcomes = models.TextField(blank=True, null=True, verbose_name='Learning outcomes', **webfield_attrs)
    selection_criteria = models.TextField(blank=True, null=True, verbose_name='Entry requirements', **webfield_attrs)
    it_requirements = models.TextField(blank=True, null=True, **webfield_attrs)
    credit_points = models.IntegerField(blank=True, null=True)
    points_level = models.ForeignKey('PointsLevel', models.DO_NOTHING, db_column='points_level', blank=True, null=True)
    enrol_online = models.BooleanField(blank=True, null=True, verbose_name='Online enrolment')
    non_credit_bearing = models.BooleanField(default=True, verbose_name='Credit bearing')
    auto_feedback = models.BooleanField(default=True)
    auto_reminder = models.BooleanField(default=True)
    no_search = models.BooleanField(default=False, verbose_name='Hide from search results')
    week_number = models.IntegerField(blank=True, null=True, help_text='For multi-week summer schools')

    custom_fee = models.CharField(
        max_length=1012,
        blank=True,
        null=True,
        help_text='Only used in the course summary box (replaces the automatic fees section on the website)',
    )
    format = models.ForeignKey(
        'ModuleFormat',
        models.DO_NOTHING,
        db_column='format',
        blank=True,
        null=True,
        help_text='Tells the student how they will study',  # todo: help link
    )

    is_cancelled = models.BooleanField(default=False)
    default_non_credit = models.BooleanField(
        default=False,
        verbose_name='Default status',
        help_text='Online enrolments will have this status by default',
    )
    note = models.CharField(max_length=512, blank=True, null=True)
    terms_and_conditions = models.IntegerField(
        choices=((1, 'Open access courses'), (2, 'Selective short courses')), default=1
    )
    apply_url = models.CharField(max_length=512, blank=True, null=True)
    further_details = models.TextField(blank=True, null=True, **webfield_attrs)
    is_repeat = models.BooleanField(default=False)
    reminder_sent_on = models.DateTimeField(blank=True, null=True)

    mailing_list = models.CharField(max_length=25, blank=True, null=True)
    notification = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        help_text='A message that appears atop the page, announcing change of tutor, date, location, etc.',
    )
    cost_centre = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text='Cost centre, activity code and source of funds form the finance code',
    )
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

    direct_enrolment = models.BooleanField(default=False)
    hash = models.CharField(default=uuid.uuid4, editable=False, null=True, max_length=40)

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
        blank=True,
    )
    marketing_types = models.ManyToManyField(
        to='MarketingType',
        through='ModuleMarketingType',
        help_text='These decide how the course is displayed in the website search results, and in print material',
        blank=True,
    )
    equipment = models.ManyToManyField(to='Equipment', through='ModuleEquipment')
    objects = ModuleManager()

    class Meta:
        db_table = 'module'
        base_manager_name = 'objects'
        permissions = [('upload_to_cabs', 'Can upload module booking details to CABS')]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.hash:
            self.hash = uuid.uuid4()  # todo: removable once modules have been back-filled with hashes
        if not self.url:
            self.url = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse('module:view', args=[self.id])

    def get_edit_url(self) -> str:
        return reverse('module:edit', args=[self.id])

    def get_website_url(self) -> str:
        return f'{settings.PUBLIC_WEBSITE_URL}/courses/{self.url}?code={self.code}'

    def get_direct_enrolment_url(self) -> str:
        """The URL for adding an enrolment direct the basket, before general enrolment is open"""
        return f'{settings.PUBLIC_WEBSITE_URL}/basket/add-module/{self.code}?_next=%2Fbasket&_enrolment={self.hash}'

    @property
    def full_time_equivalent(self) -> float:
        """Calculate FTE, depending on level
        PG courses 100: FTE = 180 credit points
        UG courses 100: FTE = 120 credit points

        Ensure points_level is included in select_related if running this on large querysets
        """
        if self.is_postgraduate:
            denominator = 180.0
        elif self.is_undergraduate:
            denominator = 120.0
        else:
            return 0.0
        return round(100 * (self.credit_points or 0) / denominator)

    @property
    def is_undergraduate(self) -> bool:
        return self.points_level and self.points_level.is_undergraduate

    @property
    def is_postgraduate(self) -> bool:
        return self.points_level and self.points_level.is_postgraduate

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
        if hasattr(self, 'proposal') and not self.proposal.is_complete:
            errors['proposal'] = 'Proposal unapproved'

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
            raise ValidationError({'start_date': 'Please set a start date'})
        elif self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'End date cannot be earlier than start date'})

        # Check if all components that make up the finance code are supplied, or none
        finance_components = [self.cost_centre, self.activity_code, self.source_of_funds]
        if any(finance_components) and not all(finance_components):
            raise ValidationError(
                {'cost_centre': 'Please provide all of cost centre, activity code and source of funds, or none'}
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
    building = models.CharField(max_length=64)
    address = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=64, blank=True)
    postcode = models.CharField(max_length=50, blank=True)
    longitude = models.FloatField(blank=True)
    latitude = models.FloatField(blank=True)

    class Meta:
        db_table = 'location'
        ordering = ('building', 'city')

    def __str__(self) -> str:
        if self.city:
            return f'{self.building}, {self.city}'
        return str(self.building)

    @property
    def full_address(self) -> str:
        """Render a complete address of the location, useful for google maps queries, for example"""
        return f'{self.building}, {self.address}, {self.city} {self.postcode}'


class Room(models.Model):
    id = models.CharField(primary_key=True, max_length=12)  # CABS ids.  Will be a problem if numbers ever clash
    size = models.IntegerField()
    bookable = models.BooleanField(default=True)
    building = models.CharField(max_length=12)  # todo: this is too low if we ever add venues
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'room'
        ordering = ['building', 'id']

    def __str__(self) -> str:
        return str(self.id)

    @property
    def long_name(self) -> str:
        return f'{self.id}, {self.building} ({self.size})'


class Book(models.Model):
    class Types(models.TextChoices):
        PREPARATORY = 'Preparatory reading', 'Preparatory reading'
        COURSE = 'Course reading', 'Course reading'
        __empty__ = '– Select –'

    module = models.ForeignKey('Module', models.CASCADE, db_column='module', related_name='books')
    title = models.CharField(max_length=512)
    author = models.CharField(max_length=512)
    type = models.CharField(max_length=24, choices=Types.choices)
    additional_information = models.CharField(max_length=512, blank=True, null=True)
    solo_link = models.CharField(max_length=512, blank=True, null=True, validators=[validators.URLValidator()])
    isbn_shelfmark = models.CharField(max_length=64, blank=True, null=True, verbose_name='ISBN / library shelfmark')
    price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    library_note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'book'

    def __str__(self) -> str:
        return str(self.title)

    def get_absolute_url(self) -> str:
        return self.module.get_absolute_url() + '#reading-list'

    def get_edit_url(self) -> str:
        return reverse('module:edit-book', kwargs={'pk': self.pk})

    def get_delete_url(self) -> str:
        return reverse('module:delete-book', kwargs={'pk': self.pk})


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


class PointsLevel(models.Model):
    """HESA table for the level of credit points provided by a module (UG, Masters, Dphil...) plus a map to FHEQ"""

    id = models.IntegerField(primary_key=True)  # hesa value
    description = models.CharField(max_length=255)
    fheq_level = models.IntegerField()

    class Meta:
        db_table = 'points_level'

    def __str__(self) -> str:
        return str(self.description)

    @property
    def is_undergraduate(self) -> bool:
        # todo: consider converting this and is_postgrad to rely on a column, adding an "None (nonaccredited)" option,
        #       and make it a notnull default for the module column.  Would simplify null-aware logic
        return self.id in (1, 2, 3)

    @property
    def is_postgraduate(self) -> bool:
        return self.id in (6, 7)


class Equipment(models.Model):
    name = models.CharField(max_length=50)
    ewert_cabs_code = models.CharField(max_length=10)
    rewley_cabs_code = models.CharField(max_length=10)
    always_required = models.BooleanField(default=False)

    class Meta:
        db_table = 'equipment'

    def __str__(self) -> str:
        return str(self.name)


class ModuleEquipment(SignatureModel):
    module = models.ForeignKey(Module, models.CASCADE, db_column='module')
    equipment = models.ForeignKey(Equipment, models.PROTECT, db_column='equipment')
    note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'module_equipment'
