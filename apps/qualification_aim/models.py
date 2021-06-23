from __future__ import annotations

from typing import Optional

from django.db import models
from django.urls import reverse

from apps.core.models import SignatureModel
from apps.core.utils.dates import academic_year

AT_PROVIDER_STUDY_LOCATION = 1
UK_DISTANCE_STUDY_LOCATION = 6
NON_UK_DISTANCE_STUDY_LOCATION = 9


class QualificationAim(SignatureModel):
    student = models.ForeignKey('student.Student', models.DO_NOTHING, db_column='student')
    programme = models.ForeignKey(
        'programme.Programme',
        models.DO_NOTHING,
        db_column='programme',
        related_name='qualification_aims',
        limit_choices_to={'is_active': True},
    )
    title = models.CharField(max_length=96)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    study_location = models.ForeignKey(
        'programme.StudyLocation',
        models.DO_NOTHING,
        db_column='study_location',
        limit_choices_to={'is_active': True},
    )
    entry_qualification = models.ForeignKey(
        'EntryQualification',
        models.DO_NOTHING,
        db_column='entry_qualification',
        null=True,
        blank=True,
        limit_choices_to=models.Q(web_publish=True) | models.Q(id__in=['X00', 'X06']),  # Todo: should be a column
    )
    reason_for_ending = models.ForeignKey(
        'ReasonForEnding', models.DO_NOTHING, db_column='reason_for_ending', blank=True, null=True
    )
    sits_code = models.CharField(max_length=12, blank=True, null=True, verbose_name='SITS code')

    class Meta:
        # managed = False
        db_table = 'qa'
        verbose_name = 'Qualification aim'

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.programme.title

        if not self.entry_qualification:
            self.entry_qualification = self.student.highest_qualification

        # Study location inherited from programmes, with logic for online students, for HESA returns
        if not self.study_location_id:
            if self.programme.study_location_id == UK_DISTANCE_STUDY_LOCATION and not self.student.domicile.is_uk:
                self.study_location_id = NON_UK_DISTANCE_STUDY_LOCATION  # Distance learning Non-UK based
            else:
                self.study_location = self.programme.study_location

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('qualification_aim:view', args=[self.pk])

    def get_edit_url(self):
        return reverse('qualification_aim:edit', args=[self.pk])

    @property
    def academic_year(self) -> Optional[int]:
        if self.start_date:
            return academic_year(self.start_date)
        return None

    def __str__(self):
        return f'{self.student}: {self.title}'

    def is_certhe(self) -> bool:
        # Todo: There must be a way to this without hardcoding statuses (old and new certhe)
        return self.programme_id in (5, 270)

    @property
    def locked_fields(self) -> list[str]:
        """Determine whether the object is managed by SITS, and thus has fields locked for editing"""
        if self.created_by == 'SITS' or self.modified_by == 'SITS' or self.sits_code:
            return ['start_date', 'end_date', 'reason_for_ending', 'title', 'programme']
        return []


class EntryQualification(models.Model):
    id = models.CharField(primary_key=True, max_length=3)  # HESA code, e.g. C90
    description = models.CharField(max_length=128)
    custom_description = models.CharField(max_length=128, blank=True, null=True)
    elq_rank = models.IntegerField()
    web_publish = models.BooleanField(db_column='web_publish')
    display_order = models.IntegerField()

    class Meta:
        # managed = False
        db_table = 'entry_qualification'
        ordering = ('display_order', 'elq_rank')

    def __str__(self):
        return f'{self.custom_description or self.description} ({self.id})'


class ReasonForEnding(SignatureModel):
    description = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'reason_for_ending'


class CertHEMarks(SignatureModel):
    qualification_aim = models.OneToOneField(
        'QualificationAim', models.DO_NOTHING, db_column='qa', related_name='certhe_marks'
    )
    courses_transferred_in = models.TextField(blank=True, null=True)
    credits_transferred_in = models.IntegerField(blank=True, null=True)
    subject = models.ForeignKey('hesa.HECoSSubject', models.DO_NOTHING, db_column='subject', blank=True, null=True)
    assignment1_date = models.DateField(blank=True, null=True)
    assignment1_grade = models.IntegerField(blank=True, null=True)
    assignment2_date = models.DateField(blank=True, null=True)
    assignment2_grade = models.IntegerField(blank=True, null=True)
    assignment3_date = models.DateField(blank=True, null=True)
    assignment3_grade = models.IntegerField(blank=True, null=True)
    journal1_date = models.DateField(blank=True, null=True)
    journal2_date = models.DateField(blank=True, null=True)
    journal_cats_points = models.IntegerField(blank=True, null=True)
    is_introductory_course = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'certhe_marks'
