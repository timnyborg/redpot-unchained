from django.core import validators
from django.db import models

from apps.core.models import SignatureModel


class HECoSSubject(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    definition = models.CharField(max_length=255, blank=True, null=True)
    cost_centre = models.ForeignKey(
        'HESACostCentre', models.DO_NOTHING, db_column='cost_centre', blank=True, null=True
    )

    class Meta:
        db_table = 'hecos_subject'
        ordering = ('name',)
        verbose_name = 'HECoS subject'

    def __str__(self) -> str:
        return str(self.name)


class ModuleHECoSSubject(SignatureModel):
    """Records the subject makeup of a module for HESA-reporting purposes"""

    module = models.ForeignKey(
        'module.Module', models.DO_NOTHING, db_column='module', related_name='module_hecos_subjects'
    )
    hecos_subject = models.ForeignKey(
        'HECoSSubject', models.DO_NOTHING, db_column='hecos_subject', verbose_name='HECoS subject'
    )
    percentage = models.IntegerField(validators=[validators.MinValueValidator(1), validators.MaxValueValidator(100)])

    class Meta:
        db_table = 'module_hecos_subject'


class ProgrammeHecosSubject(models.Model):
    programme = models.ForeignKey('programme.Programme', models.DO_NOTHING, db_column='programme')
    hecos_subject = models.ForeignKey('HECoSSubject', models.DO_NOTHING, db_column='hecos_subject')
    percentage = models.IntegerField()

    class Meta:
        db_table = 'programme_hecos_subject'
        ordering = ('programme', 'hecos_subject')
        verbose_name = 'Programme HECoS subject'


class HESACostCentre(models.Model):
    description = models.CharField(max_length=64, blank=True, null=True)
    price_group = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        db_table = 'hesa_cost_centre'
        ordering = ('description',)
        verbose_name = 'HESA cost centre'

    def __str__(self) -> str:
        return f'{self.description}: {self.price_group}'
