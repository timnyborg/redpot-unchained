from django.db import models


class Payment(models.Model):
    student = models.IntegerField()
    payment_ref = models.TextField()
    discount_code = models.TextField(blank=True, null=True)
    event = models.IntegerField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    firstname = models.TextField(blank=True, null=True)
    surname = models.TextField(blank=True, null=True)
    email = models.TextField()
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    address3 = models.TextField(blank=True, null=True)
    town = models.TextField(blank=True, null=True)
    county = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    postcode = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.TextField()
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.TextField(blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.TextField(blank=True, null=True)
    voucher = models.IntegerField(blank=True, null=True)
    voucher_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'payment'
        managed = False


class PaymentItem(models.Model):
    payment = models.ForeignKey(Payment, models.DO_NOTHING, db_column='payment')
    student = models.IntegerField(blank=True, null=True)
    enrolment = models.IntegerField(blank=True, null=True)
    code = models.TextField(blank=True, null=True)
    firstname = models.TextField(blank=True, null=True)
    surname = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    hash_id = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    entry_qualification = models.CharField(primary_key=True, max_length=3)
    fees = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    domicile = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'payment_item'
        managed = False
