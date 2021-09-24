from datetime import datetime

from django.db import models
from django.db.models import Case, Min, Q, Value, When
from django.db.models.functions import Replace

from apps.core.models import SignatureModel
from apps.module.models import Module


class DiscountQuerySet(models.QuerySet):
    def matching_module(self, module: Module) -> models.QuerySet:
        # Limit the set to unexpired discounts which apply to a module
        return self.annotate(search_module_code=Value(module.code, output_field=models.CharField())).filter(
            # Get unexpired discounts, limited to this portfolio if required
            Q(expires_on=None) | Q(expires_on__gt=datetime.now()),
            Q(portfolio=module.portfolio_id) | Q(portfolio=None),
            # We currently allow use of * in place of %
            search_module_code__like=Replace('module_mask', Value('*'), Value('%')),
        )

    def with_eligibility(self) -> models.QuerySet:
        # Adds a boolean column 'all_eligible', which is True if all students can use a code
        return self.annotate(
            # 0 indicates all students
            Min('student__student'),
            all_eligible=Case(
                When(student__student__min=0, then=True),
                default=False,
                output_field=models.BooleanField(),
            ),
        )


class Discount(SignatureModel):
    name = models.TextField()
    code = models.CharField(max_length=20, unique=True)
    percent = models.IntegerField()
    usable_once = models.BooleanField(default=False)
    expires_on = models.DateField(blank=True, null=True)
    module_mask = models.CharField(max_length=20)
    portfolio = models.ForeignKey('core.Portfolio', models.DO_NOTHING, db_column='portfolio', blank=True, null=True)

    objects = DiscountQuerySet.as_manager()

    class Meta:
        db_table = 'discount'

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return '#'

    def get_edit_url(self):
        return '#'


class DiscountStudent(models.Model):
    discount = models.ForeignKey(
        Discount, models.DO_NOTHING, db_column='discount', related_name='students', related_query_name='student'
    )
    student = models.IntegerField()
    redeemed = models.BooleanField(default=False)
    expires_on = models.DateField(blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'discount_student'
