from django.db import models
from django.core.validators import RegexValidator
from django.db.models import Model, CharField, DateField, ForeignKey, IntegerField, BooleanField, ImageField, DO_NOTHING, Q
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.functional import cached_property
from apps.main.models import SignatureModel


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


class Module(SignatureModel, Model):
    code = CharField(max_length=12, help_text='For details on codes, see <link>')    
    title = CharField(max_length=80)
    url = models.SlugField(max_length=256, blank=True, null=True)
    
    start_date = DateField(blank=True, null=True)
    end_date = DateField(blank=True, null=True)

    michaelmas_end = DateField(blank=True, null=True)
    hilary_start = DateField(blank=True, null=True)

    division = ForeignKey('programme.Division', DO_NOTHING, db_column='division',
                          limit_choices_to=Q(id__gt=8) | Q(id__lt=5), default=1)
    portfolio = ForeignKey('programme.Portfolio', DO_NOTHING, db_column='portfolio', default=1)
    
    status = ForeignKey('ModuleStatus', DO_NOTHING, db_column='status', default=10)
    max_size = IntegerField(blank=True, null=True)

    image = ImageField(upload_to='uploads/%Y/%m/%d/', max_length=512, blank=True, null=True)

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
    application = models.TextField(blank=True, null=True)
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

    def long_form(self):
        if self.start_date:
            return f'{self.code} - {self.title} ({self.start_date:%d %b %Y})'
        return f'{self.code} - {self.title}'

    @cached_property
    def places_taken(self):
        return self.enrolments.filter(status__takes_place=True).count()

    def finance_code(self):
        if self.cost_centre and self.activity_code and self.source_of_funds:
            return f'{self.cost_centre} {self.activity_code} {self.source_of_funds}'
            
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

        # # Check if all components that make up the finance code are supplied, or none
        # components = ['cost_centre', 'activity_code', 'source_of_funds']
        # if any(self.__attr__(field) for field in components) and not all(self.__attr__(field) for field in components):
            # for field in components:
                # if not self.__attr__(field):
                    # raise ValidationError({
                        # field: 'Please provide all of cost centre, activity code and source of funds, or neither',
                    # })

        # if not all(self.__attr__(field) for field in components) and self.enrol_online:
            # raise ValidationError({
                # 'enrol_online': 'Online enrolment disallowed without cost centre, activity code and source of funds',
            # })


class ModuleStatus(Model):
    id = IntegerField(primary_key=True)
    description = CharField(max_length=64, blank=True, null=True)
    publish = BooleanField(blank=True, null=True)
    short_desc = CharField(max_length=50, blank=True, null=True)
    waiting_list = BooleanField(blank=True, null=True)   

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
        return self.building


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
