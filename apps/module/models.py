from __future__ import annotations

from datetime import datetime
from enum import IntEnum
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
from redpot.settings import PUBLIC_WEBSITE_URL


class Statuses(IntEnum):
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
    use_for_related_fields = True
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

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).defer(*self.defer_fields)


class Module(SignatureModel, models.Model):
    code = models.CharField(max_length=12, help_text='For details on codes, see <link>')
    title = models.CharField(max_length=80)
    url = models.SlugField(max_length=256, blank=True, null=True)

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    michaelmas_end = models.DateField(blank=True, null=True)
    hilary_start = models.DateField(blank=True, null=True)

    division = models.ForeignKey('programme.Division', models.DO_NOTHING, db_column='division',
                                 limit_choices_to=models.Q(id__gt=8) | models.Q(id__lt=5), default=1)
    portfolio = models.ForeignKey('programme.Portfolio', models.DO_NOTHING, db_column='portfolio', default=1)

    status = models.ForeignKey('ModuleStatus', models.DO_NOTHING, db_column='status', default=10)
    max_size = models.IntegerField(blank=True, null=True)

    image = models.ImageField(upload_to='uploads/%Y/%m/%d/', max_length=512, blank=True, null=True)

    # type = models.ForeignKey('ModuleType', models.DO_NOTHING, db_column='type', blank=True, null=True)

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
    # finance_code = models.CharField(max_length=64, blank=True, null=True)
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
    # terms_and_conditions = models.ForeignKey('TermsAndConditions', models.DO_NOTHING, db_column='terms_and_conditions')
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
        max_length=2, blank=True, null=True,
        validators=[RegexValidator(r'^\d{2}$', message='Invalid code')],
        help_text='e.g. 00',
    )
    source_of_funds = models.CharField(
        max_length=5, blank=True, null=True,
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
    subjects = models.ManyToManyField(
        to='Subject',
        through='ModuleSubject',
    )
    marketing_types = models.ManyToManyField(
        to='MarketingType',
        through='ModuleMarketingType',
    )
    objects = ModuleManager()

    class Meta:
        # managed = False
        db_table = 'module'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.url:
            self.url = slugify(self.title)
        # if self.status == 33: # cancelled
            # self.is_cancelled = True
            # self.auto_publish = False
        # self.update_status()  # Date changes may alter auto-status.

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('module:view', args=[self.id])

    def get_edit_url(self):
        return reverse('module:edit', args=[self.id])

    def get_website_url(self):
        return f'{PUBLIC_WEBSITE_URL}/courses/{self.url}?code={self.code}'

    @property
    def long_form(self):
        if self.start_date:
            return f'{self.code} - {self.title} ({self.start_date:%d %b %Y})'
        return f'{self.code} - {self.title}'

    @cached_property
    def places_taken(self):
        return self.enrolments.filter(status__takes_place=True).count()

    def is_full(self):
        return self.max_size and self.places_taken() >= self.max_size

    @property
    def finance_code(self):
        if self.cost_centre and self.activity_code and self.source_of_funds:
            return f'{self.cost_centre} {self.activity_code} {self.source_of_funds}'

    def other_runs(self):
        # Provides a list of other module runs, if url is set
        if self.url:
            return (
                Module.objects
                .filter(url=self.url, division=self.division)
                .exclude(id=self.id)
                .order_by(F('start_date').desc(nulls_last=True))
            )
        return Module.objects.none()

    def next_run(self) -> Optional[Module]:
        if self.start_date:
            return self.other_runs().filter(
                is_published=True,
                start_date__gte=self.start_date
            ).order_by('-start_date').first()

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
        if not self.custom_fee and not self.fees.filter(
            is_visible=True, type__is_tuition=True, eu_fee=False
        ).exists():
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
            'errors': errors
        }

    @property
    def is_publishable(self):
        return self._publish_check['success']

    @property
    def publish_errors(self):
        return self._publish_check['errors']

    @cached_property
    def prospectus_check(self, prospectus_year: int = None) -> dict:
        """Checks if a module will be included in a year's prospectus (the upcoming academic year, by default)"""
        if not prospectus_year:
            prospectus_year = academic_year() + 1

        # We only include one academic year, hiding any cancelled or non-searchable courses
        in_scope = (
            academic_year(self.start_date) == prospectus_year
            and not self.is_cancelled
            and not self.no_search
        )

        errors = {}
        if in_scope:
            if not self.format_id:
                errors['format'] = 'Format required'
            if not self.snippet:
                errors['snippet'] = 'Snippet required'
            if not self.custom_fee and not self.fees.filter(
                is_visible=True, type__is_tuition=True, eu_fee=False
            ).exists():
                errors['fee'] = 'Published non-EU programme fee required'
            if not self.subjects.exists():
                errors['subject'] = 'Missing a marketing subject'

        return {
            'success': in_scope and not errors,
            'errors': errors,
            'year': prospectus_year,
            'included': in_scope
        }

    def _get_auto_status(self):
        now = datetime.now()
        today = now.date()

        # Automatic date logic
        if self.publish_date > today:
            # Todo: determine if this has any value
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

    def update_status(self):
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

                self.status = self._get_auto_status()

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
                # if not self.is_published and idb.module_status(self.status_id).publish:
                #     _check_ongoing_proposal(self.id)
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

    def clean(self):
        # Check both term start/end date fields are filled, or neither
        if bool(self.hilary_start) != bool(self.michaelmas_end):
            raise ValidationError({
                'hilary_start': 'You must provide both term dates',
                'michaelmas_end': 'You must provide both term dates',
            })

        # Check end_date is equal or later to start_date
        if self.end_date and not self.start_date:
            raise ValidationError({
                'start_date': 'Please set a start date',
            })
        elif self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({
                'end_date': 'End date cannot be earlier than start date',
            })

        # Check if all components that make up the finance code are supplied, or none
        finance_components = [self.cost_centre, self.activity_code, self.source_of_funds]
        if any(finance_components) and not all(finance_components):
            raise ValidationError({
                'cost_centre': 'Please provide all of cost centre, activity code and source of funds, or none',
            })

        if not all(finance_components) and self.enrol_online:
            raise ValidationError({
                'enrol_online': 'Online enrolment disallowed without cost centre, activity code and source of funds',
            })


class ModuleStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(max_length=64, blank=True, null=True)
    publish = models.BooleanField(blank=True, null=True)
    short_desc = models.CharField(max_length=50, blank=True, null=True)
    waiting_list = models.BooleanField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'module_status'
        ordering = ['id']

    def __str__(self):
        return self.description


class FeeType(models.Model):
    id = models.IntegerField(primary_key=True)
    narrative = models.CharField(max_length=64, blank=True, null=True)
    # account = models.ForeignKey('LedgerAccount', models.DO_NOTHING, db_column='account', blank=True, null=True)
    display_order = models.IntegerField(blank=True, null=True)
    is_tuition = models.BooleanField()
    is_active = models.IntegerField()

    class Meta:
        # managed = False
        db_table = 'fee_type'


class Fee(SignatureModel):
    module = models.ForeignKey('Module', models.DO_NOTHING, db_column='module', related_name='fees')
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    type = models.ForeignKey('FeeType', models.DO_NOTHING, db_column='type')
    description = models.CharField(max_length=64)
    finance_code = models.CharField(max_length=64, blank=True, null=True)
    account = models.CharField(max_length=64)
    eu_fee = models.BooleanField(db_column='eufee')
    is_visible = models.BooleanField()
    is_payable = models.BooleanField()
    is_compulsory = models.BooleanField()
    is_catering = models.BooleanField(blank=True, null=True)
    is_single_accom = models.BooleanField(blank=True, null=True)
    is_twin_accom = models.BooleanField(blank=True, null=True)
    credit_fee = models.BooleanField()
    end_date = models.DateField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
    allocation = models.IntegerField(blank=True, null=True)

    catering_bookings = models.ManyToManyField(
        'enrolment.Enrolment',
        through='enrolment.Catering',
    )

    def catering_booking_count(self):
        return self.catering_bookings.filter(status__takes_place=True).count()

    class Meta:
        # managed = False
        db_table = 'fee'

    def __str__(self):
        return self.description


class ModuleFormat(models.Model):
    description = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'module_format'

    def __str__(self):
        return self.description


class Location(SignatureModel):
    address = models.CharField(max_length=128)
    city = models.CharField(max_length=64, blank=True, null=True)
    postcode = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    building = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'location'

    def __str__(self):
        if self.city and self.building:
            return f'{self.building}, {self.city}'
        elif self.building:
            return self.building
        return 'Invalid: no city or building'


class ModuleWaitlist(models.Model):
    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module', related_name='waitlist')
    student = models.ForeignKey('student.Student', models.DO_NOTHING, db_column='student')
    listed_on = models.DateTimeField(auto_now_add=True)
    emailed_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'module_waitlist'

    def get_absolute_url(self):
        return '#'

    def get_edit_url(self):
        return '#'

    def get_delete_url(self):
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
        # managed = False
        db_table = 'book'

    def get_absolute_url(self):
        return '#'

    def get_edit_url(self):
        return '#'

    def get_delete_url(self):
        return '#'


class BookStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    status = models.TextField()

    class Meta:
        # managed = False
        db_table = 'book_status'

    def __str__(self):
        return self.status


class Subject(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    area = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'subject'

    def __str__(self):
        return self.name

    def long_form(self):
        return f'{self.name} ({self.area})'


class ModuleSubject(models.Model):
    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module')
    subject = models.ForeignKey('Subject', models.DO_NOTHING, db_column='subject')

    class Meta:
        # managed = False
        db_table = 'module_subject'
        unique_together = (('module', 'subject'),)


class MarketingType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'marketing_type'

    def __str__(self):
        return self.name


class ModuleMarketingType(models.Model):
    marketing_type = models.ForeignKey(MarketingType, models.DO_NOTHING, db_column='marketing_type')
    module = models.ForeignKey(Module, models.DO_NOTHING, db_column='module')

    class Meta:
        # managed = False
        db_table = 'module_marketing_type'
        unique_together = (('module', 'marketing_type'),)
