from django.db import models
from django.urls import reverse

from apps.core.models import SignatureModel
from apps.core.utils.web2py_compat import PipeSeparatedIntegersField, PipeSeparatedStringsField
from apps.module.models import RoomSetups


class Statuses(models.IntegerChoices):
    CREATED = 1, 'Created'
    TUTOR = 2, 'Tutor'
    DOS = 3, 'DoS'
    ADMIN = 4, 'Admin'
    COMPLETE = 5, 'Complete'


class Proposal(SignatureModel):
    module = models.OneToOneField('module.Module', models.DO_NOTHING, db_column='module')
    status = models.IntegerField(choices=Statuses.choices, default=Statuses.CREATED)
    title = models.CharField(max_length=80)
    subjects = PipeSeparatedIntegersField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    michaelmas_end = models.DateField(blank=True, null=True, verbose_name='End of first term')
    hilary_start = models.DateField(blank=True, null=True, verbose_name='Start of second term')
    end_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    no_meetings = models.IntegerField(blank=True, null=True, verbose_name='# of meetings')
    duration = models.FloatField(blank=True, null=True)
    is_repeat = models.BooleanField(blank=True, null=True, verbose_name='Is this a repeat course?')
    previous_run = models.CharField(max_length=12, blank=True, null=True)
    location = models.ForeignKey(
        'module.Location', on_delete=models.PROTECT, blank=True, null=True, db_column='location'
    )
    address = models.CharField(max_length=255, blank=True, null=True)
    room = models.ForeignKey('module.Room', on_delete=models.PROTECT, db_column='room', blank=True, null=True)
    room_setup = models.CharField(
        max_length=12,
        choices=RoomSetups.choices,
        null=True,
        verbose_name='Classroom layout',
        default=RoomSetups.SEMINR,
    )
    max_size = models.IntegerField(blank=True, null=True, verbose_name='Class size')
    reduced_size = models.IntegerField(blank=True, null=True)
    reduction_reason = models.CharField(max_length=50, blank=True, null=True, verbose_name='Reason for reduction')
    tutor = models.ForeignKey('tutor.Tutor', on_delete=models.PROTECT, db_column='tutor')
    tutor_title = models.CharField(max_length=16, blank=True, null=True)
    tutor_firstname = models.CharField(max_length=40, null=True)
    tutor_nickname = models.CharField(max_length=64, blank=True, null=True)
    tutor_surname = models.CharField(max_length=40, null=True)
    tutor_qualifications = models.CharField(max_length=256, blank=True, null=True)
    tutor_biography = models.TextField(blank=True, null=True)
    field_trips = models.CharField(max_length=60, blank=True, null=True)
    risk_form = models.CharField(max_length=255, blank=True, null=True, verbose_name='Risk assessment form')
    snippet = models.TextField(blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    programme_details = models.TextField(blank=True, null=True)
    course_aims = models.TextField(blank=True, null=True)
    level_and_demands = models.TextField(blank=True, null=True)
    assessment_methods = models.TextField(blank=True, null=True)
    teaching_methods = models.TextField(blank=True, null=True)
    teaching_outcomes = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    equipment = PipeSeparatedIntegersField(blank=True, null=True, verbose_name='Required equipment')
    scientific_equipment = models.CharField(max_length=64, blank=True, null=True)
    additional_requirements = models.TextField(blank=True, null=True, verbose_name='Additional class requirements')
    recommended_reading = models.TextField(blank=True, null=True)
    dos = models.ForeignKey(
        'core.User',
        on_delete=models.PROTECT,
        db_column='dos',
        blank=True,
        null=True,
        verbose_name='Director of studies',
        to_field='username',
    )
    due_date = models.DateField(blank=True, null=True, verbose_name='Tutor completion due')
    grammar_points = models.TextField(blank=True, null=True)
    limited = models.BooleanField(
        default=False, verbose_name='Is this a language course?', help_text='Updatable fields will be limited'
    )
    updated_fields = PipeSeparatedStringsField(blank=True, null=True)
    tutor_approve = models.DateTimeField(blank=True, null=True)
    dos_approve = models.DateTimeField(blank=True, null=True)
    admin_approve = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    reminded_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'proposal'
        verbose_name = 'Course proposal'
        permissions = [('approve_proposal', 'Can approve course proposals (when assigned as Director of Studies)')]

    def __str__(self) -> str:
        return f'#{self.pk}: {self.title}'

    def get_edit_url(self) -> str:
        return reverse('proposal:edit', kwargs={'pk': self.pk})

    def get_delete_url(self) -> str:
        return reverse('proposal:delete', kwargs={'pk': self.pk})

    @property
    def is_complete(self) -> bool:
        return self.status == Statuses.COMPLETE


class ProposalMessage(models.Model):
    proposal = models.IntegerField()
    sender = models.CharField(max_length=16)
    sent_on = models.DateTimeField()
    message = models.TextField()

    class Meta:
        db_table = 'proposal_message'
