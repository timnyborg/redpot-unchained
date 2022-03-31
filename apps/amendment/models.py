from datetime import datetime

from django.db import models
from django.urls import reverse


class Amendment(models.Model):
    type = models.ForeignKey('AmendmentType', models.DO_NOTHING, db_column='type')
    status = models.ForeignKey('AmendmentStatus', models.DO_NOTHING, db_column='status', default=1)
    enrolment = models.ForeignKey(
        'enrolment.Enrolment',
        models.DO_NOTHING,
        db_column='enrolment',
        related_name='amendments',
        related_query_name='amendment',
    )
    requested_on = models.DateTimeField(default=datetime.now)
    requested_by = models.ForeignKey(
        'core.User',
        on_delete=models.DO_NOTHING,
        db_column='requested_by',  # todo: implement fk on legacy db, or move to an id fk
        related_name='change_requests',
        related_query_name='change_request',
        to_field='username',
    )
    approved_on = models.DateTimeField(blank=True, null=True)
    approved_by = models.TextField(blank=True, null=True)
    executed_on = models.DateTimeField(blank=True, null=True)
    executed_by = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    details = models.TextField(blank=True, null=True)
    approver = models.ForeignKey(
        'core.User',
        on_delete=models.DO_NOTHING,
        db_column='approver',  # todo: implement fk on legacy db, or move to an id fk
        related_name='approver_change_requests',
        related_query_name='approver_change_request',
        to_field='username',
        null=True,
    )
    # Todo: convert to foreign-key and replace 'multiple' with an empty_label and details validation in forms
    transfer_module = models.TextField(blank=True, null=True)
    transfer_enrolment = models.ForeignKey(
        'enrolment.Enrolment',
        models.DO_NOTHING,
        db_column='transfer_enrolment',
        blank=True,
        null=True,
        related_name='+',
    )
    invoice = models.ForeignKey(
        'invoice.Invoice', models.DO_NOTHING, db_column='invoice', blank=True, null=True, related_name='+'
    )
    source_invoice = models.IntegerField(blank=True, null=True)
    transfer_invoice = models.ForeignKey(
        'invoice.Invoice', models.DO_NOTHING, db_column='transfer_invoice', blank=True, null=True, related_name='+'
    )
    reason = models.ForeignKey(
        'AmendmentReason', models.DO_NOTHING, db_column='reason', null=True  # Null allowed for print-only
    )
    batch = models.IntegerField(blank=True, null=True)
    narrative = models.CharField(max_length=128)
    is_complete = models.BooleanField(
        default=False,
        help_text='Once marked complete, the request will no longer be editable',
        verbose_name='Mark complete',
    )
    actioned_online = models.BooleanField(default=False)

    class Meta:
        db_table = 'amendment'
        permissions = [
            ('approve', 'Approve finance change requests'),
            ('edit_finance', 'Mark finance change requests complete and edit related fields'),
        ]
        verbose_name = 'Finance change request'

    def get_edit_url(self) -> str:
        return reverse('amendment:edit', kwargs={'pk': self.pk})

    def get_delete_url(self) -> str:
        return reverse('amendment:delete', kwargs={'pk': self.pk})

    @property
    def can_apply_refund(self) -> bool:
        """Indicates if the amendment can have a refund automatically generated"""
        return self.type_id == AmendmentTypes.ONLINE_REFUND and self.status_id == AmendmentStatuses.APPROVED


class AmendmentReason(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.ForeignKey('AmendmentType', on_delete=models.PROTECT, db_column='type')
    reason = models.TextField()

    class Meta:
        db_table = 'amendment_reason'

    def __str__(self) -> str:
        return str(self.reason)


class AmendmentStatuses(models.IntegerChoices):
    RAISED = 1
    APPROVED = 2
    COMPLETE = 3


class AmendmentStatus(models.Model):
    id = models.IntegerField(primary_key=True)
    status = models.TextField()
    icon = models.TextField()

    class Meta:
        db_table = 'amendment_status'

    def __str__(self) -> str:
        return str(self.status)


class AmendmentTypes(models.IntegerChoices):
    TRANSFER = 1
    AMENDMENT = 2
    ONLINE_REFUND = 3
    CREDIT_CARD_REFUND = 4
    RCP_REFUND = 5
    OTHER_REFUND = 6
    BANK_REFUND = 7


TYPES_REFUNDABLE_ONLINE = {AmendmentTypes.ONLINE_REFUND, AmendmentTypes.RCP_REFUND}


class AmendmentType(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.TextField()
    action = models.TextField()

    class Meta:
        db_table = 'amendment_type'

    def __str__(self) -> str:
        return str(self.type)
