from django.db import models


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
    requested_on = models.DateTimeField()
    requested_by = models.TextField()
    approved_on = models.DateTimeField(blank=True, null=True)
    approved_by = models.TextField(blank=True, null=True)
    executed_on = models.DateTimeField(blank=True, null=True)
    executed_by = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    details = models.TextField(blank=True, null=True)
    approver = models.CharField(max_length=16, blank=True, null=True)
    transfer_module = models.TextField(blank=True, null=True)
    transfer_enrolment = models.ForeignKey(
        'enrolment.Enrolment',
        models.DO_NOTHING,
        db_column='transfer_enrolment',
        blank=True,
        null=True,
        related_name='+',
    )
    invoice = models.IntegerField(blank=True, null=True)
    source_invoice = models.IntegerField(blank=True, null=True)
    transfer_invoice = models.IntegerField(blank=True, null=True)
    reason = models.ForeignKey('AmendmentReason', models.DO_NOTHING, db_column='reason')  # Null allowed for print-only
    batch = models.IntegerField(blank=True, null=True)
    narrative = models.CharField(max_length=128)
    is_complete = models.BooleanField(default=False)
    actioned_online = models.BooleanField(default=False)

    class Meta:
        db_table = 'amendment'
        permissions = [('approve', 'Approve finance change requests')]
        verbose_name = 'Finance change request'

    def get_edit_url(self):
        return '#'


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


class AmendmentType(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.TextField()
    action = models.TextField()
    supported = models.BooleanField()  # todo: better name for this? or at least an explanation

    class Meta:
        db_table = 'amendment_type'

    def __str__(self) -> str:
        return str(self.type)
