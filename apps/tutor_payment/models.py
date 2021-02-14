from django.db import models


class TutorFee(models.Model):
    tutor_module = models.ForeignKey(
        'tutor.TutorModule', models.DO_NOTHING, db_column='tutor_module',
        related_name='payments', related_query_name='payment'
    )
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    type = models.ForeignKey('TutorFeeType', models.DO_NOTHING, db_column='type', limit_choices_to={'is_active': True})
    pay_after = models.DateField(blank=True, null=True)
    status = models.ForeignKey('TutorFeeStatus', models.DO_NOTHING, db_column='status')
    details = models.CharField(max_length=500, blank=True, null=True)
    batch = models.PositiveIntegerField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    hours_worked = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    weeks = models.IntegerField(blank=True, null=True)
    approver = models.CharField(max_length=32)

    raised_by = models.CharField(max_length=50, editable=False)
    raised_on = models.DateTimeField(editable=False)
    approved_by = models.CharField(max_length=50, blank=True, null=True, editable=False)
    approved_on = models.DateTimeField(blank=True, null=True, editable=False)
    transferred_by = models.CharField(max_length=50, blank=True, null=True, editable=False)
    transferred_on = models.DateTimeField(blank=True, null=True, editable=False)

    class Meta:
        # managed = False
        db_table = 'tutor_fee'


class TutorFeeRate(models.Model):
    tag = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    type = models.CharField(max_length=64, null=True)  # A label used for grouping
    description = models.CharField(max_length=128)

    class Meta:
        # managed = False
        db_table = 'tutor_fee_rate'

    def __str__(self):
        return self.description


class TutorFeeStatus(models.Model):
    description = models.CharField(max_length=50, blank=True, null=True)
    paid = models.BooleanField()

    class Meta:
        # managed = False
        db_table = 'tutor_fee_status'

    def __str__(self):
        return self.description


class TutorFeeType(models.Model):
    description = models.CharField(max_length=64, blank=True, null=True)
    is_hourly = models.BooleanField()
    code = models.CharField(max_length=64, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'tutor_fee_type'

    def __str__(self):
        return self.description
