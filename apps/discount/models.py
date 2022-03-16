from datetime import datetime

from django.core import validators
from django.db import models
from django.db.models import Case, Min, Q, Value, When
from django.db.models.functions import Replace
from django.urls import reverse
from django.utils.safestring import mark_safe

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
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=20, unique=True)
    percent = models.IntegerField(validators=[validators.MinValueValidator(1), validators.MaxValueValidator(100)])
    usable_once = models.BooleanField(default=False, verbose_name='Usable only once?')
    expires_on = models.DateField(blank=True, null=True)
    module_mask = models.CharField(
        max_length=20,
        help_text=mark_safe('Limits the discount to modules matching the pattern, e.g. <i>O2[0123]P%V</i>'),
    )
    portfolio = models.ForeignKey(
        'core.Portfolio', models.DO_NOTHING, db_column='portfolio', blank=True, null=True, help_text='Optional'
    )

    objects = DiscountQuerySet.as_manager()

    class Meta:
        db_table = 'discount'

    def __str__(self) -> str:
        return str(self.name)

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        self.module_mask = self.module_mask.upper()
        super().save(*args, **kwargs)

    def get_edit_url(self) -> str:
        return reverse('discount:edit', kwargs={'pk': self.pk})

    def get_delete_url(self) -> str:
        return reverse('discount:delete', kwargs={'pk': self.pk})


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
