from django.db import models
from apps.main.models import SignatureModel


class Discount(SignatureModel):
    name = models.TextField()
    code = models.CharField(max_length=20, unique=True)
    percent = models.IntegerField(blank=True, null=True)
    usable_once = models.BooleanField(blank=True, null=True)
    expires_on = models.DateField(blank=True, null=True)
    module_mask = models.CharField(max_length=20)
    portfolio = models.ForeignKey('programme.Portfolio', models.DO_NOTHING, db_column='portfolio', blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'discount'

    def __str__(self):
        return self.name


class DiscountStudent(models.Model):
    discount = models.ForeignKey(
        Discount, models.DO_NOTHING, db_column='discount',
        related_name='students', related_query_name='student'
    )
    student = models.IntegerField()
    redeemed = models.BooleanField(blank=True, null=True)
    expires_on = models.DateField(blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'discount_student'
