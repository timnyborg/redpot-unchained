from django.db import models
from django.urls import reverse

from apps.core.models import SignatureModel
from apps.core.utils.json import ExtendedJSONDecoder, ExtendedJSONEncoder


class Types(models.TextChoices):
    CASUAL_TEACHING = 'casual', 'Casual teaching contract'
    GUEST_SPEAKER = 'guest', 'Guest speaker letter'


class Statuses(models.IntegerChoices):
    DRAFT = 1, 'Draft'
    AWAITING_APPROVAL = 2, 'Awaiting approval'
    APPROVED_AWAITING_SIGNATURE = 3, 'Approved by manager, awaiting signature'
    SIGNED_BY_DEPARTMENT = 4, 'Signed by Department'
    SIGNED_AND_RETURNED_BY_TUTOR = 5, 'Signed and returned by tutor'
    CANCELLED = 6, 'Cancelled'


class Contract(SignatureModel):
    tutor_module = models.ForeignKey('tutor.TutorModule', models.PROTECT, db_column='tutor_module')
    type = models.CharField(max_length=32, choices=Types.choices)
    options = models.JSONField(decoder=ExtendedJSONDecoder, encoder=ExtendedJSONEncoder)
    status = models.IntegerField(db_column='status', choices=Statuses.choices, default=Statuses.DRAFT)
    received_on = models.DateTimeField(blank=True, null=True)
    approver = models.ForeignKey(
        'core.User',
        on_delete=models.DO_NOTHING,
        db_column='approver',  # todo: implement fk on legacy db, or move to an id fk
        related_name='approver_contracts',
        related_query_name='approver_contract',
        to_field='username',
        verbose_name='Approving manager',
    )
    approved_by = models.CharField(max_length=32, blank=True, null=True)
    approved_on = models.DateTimeField(blank=True, null=True)
    signed_by = models.CharField(max_length=32, blank=True, null=True)
    signed_on = models.DateTimeField(blank=True, null=True)
    email_notification = models.EmailField(
        max_length=32,
        blank=True,
        null=True,
        help_text='Enter your email address to be notified when the contract is signed by the departmental signatory',
    )

    class Meta:
        db_table = 'tutor_contract'
        permissions = [('approve', 'Can be assigned and approve tutor contracts')]

    def __str__(self) -> str:
        return f'{self.get_type_display()} (#{self.pk})'

    def get_absolute_url(self) -> str:
        return reverse('contract:view', kwargs={'pk': self.pk})

    def get_edit_url(self) -> str:
        return reverse('contract:edit', kwargs={'pk': self.pk})

    def get_delete_url(self) -> str:
        return reverse('contract:delete', kwargs={'pk': self.pk})

    @property
    def is_editable(self) -> bool:
        return self.status <= Statuses.APPROVED_AWAITING_SIGNATURE

    @property
    def is_approved(self) -> bool:
        return self.status in (
            Statuses.APPROVED_AWAITING_SIGNATURE,
            Statuses.SIGNED_BY_DEPARTMENT,
            Statuses.SIGNED_AND_RETURNED_BY_TUTOR,
        )

    @property
    def is_signed(self) -> bool:
        return self.status in (Statuses.SIGNED_BY_DEPARTMENT, Statuses.SIGNED_AND_RETURNED_BY_TUTOR)
