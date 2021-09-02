from __future__ import annotations

from typing import Optional

from django.db import models
from django.urls import reverse

from apps.core.models import SignatureModel, SITSLockingModelMixin
from apps.core.utils.dates import academic_year

AT_PROVIDER_STUDY_LOCATION = 1
UK_DISTANCE_STUDY_LOCATION = 6
NON_UK_DISTANCE_STUDY_LOCATION = 9


class QualificationAim(SITSLockingModelMixin, SignatureModel):
    sits_managed_fields = ['start_date', 'end_date', 'reason_for_ending', 'title', 'programme']
    student = models.ForeignKey(
        'student.Student',
        models.DO_NOTHING,
        db_column='student',
        related_name='qualification_aims',
        related_query_name='qa',
    )
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
        related_name='qualification_aims',
        limit_choices_to=models.Q(web_publish=True) | models.Q(id__in=['X00', 'X06']),  # Todo: should be a column
    )
    reason_for_ending = models.ForeignKey(
        'ReasonForEnding',
        models.DO_NOTHING,
        db_column='reason_for_ending',
        blank=True,
        null=True,
        related_name='qualification_aims',
    )
    sits_code = models.CharField(
        max_length=12, blank=True, null=True, verbose_name='SITS code', help_text="Maps to SITS' enrolment code"
    )

    class Meta:
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

    def get_delete_url(self):
        return reverse('qualification_aim:delete', args=[self.pk])

    @property
    def academic_year(self) -> Optional[int]:
        if self.start_date:
            return academic_year(self.start_date)
        return None

    def __str__(self):
        return f'{self.student}: {self.title}'

    @property
    def is_sits_record(self) -> bool:
        """Determine whether the object originates in SITS"""
        return self.created_by == 'SITS' or self.modified_by == 'SITS' or self.sits_code is not None


class EntryQualification(models.Model):
    id = models.CharField(primary_key=True, max_length=3)  # HESA code, e.g. C90
    description = models.CharField(max_length=128)
    custom_description = models.CharField(max_length=128, blank=True, null=True)
    elq_rank = models.IntegerField()
    web_publish = models.BooleanField(db_column='web_publish')
    display_order = models.IntegerField()

    class Meta:
        db_table = 'entry_qualification'
        ordering = ('display_order', 'elq_rank')

    def __str__(self):
        return f'{self.custom_description or self.description} ({self.id})'


class ReasonForEnding(SignatureModel):
    description = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'reason_for_ending'


class CertHEMarks(SignatureModel):
    SUBJECTS = {
        100299: 'Archaeology',
        100306: 'Art history',
        100782: 'Architectural history',
        100302: 'History',
        101037: 'Literature',
        100046: 'Creative writing',
        100337: 'Philosophy',
        100601: 'Political economy',
    }

    qualification_aim = models.OneToOneField(
        'QualificationAim', models.DO_NOTHING, db_column='qa', related_name='certhe_marks'
    )
    courses_transferred_in = models.TextField(blank=True, null=True)
    credits_transferred_in = models.IntegerField(blank=True, null=True)
    subject = models.ForeignKey(
        'hesa.HECoSSubject',
        models.DO_NOTHING,
        db_column='subject',
        blank=True,
        null=True,
        limit_choices_to={'id__in': SUBJECTS},
    )
    assignment1_date = models.DateField(blank=True, null=True, verbose_name='Assignment 1 date')
    assignment1_grade = models.IntegerField(blank=True, null=True, verbose_name='Assignment 1 grade')
    assignment2_date = models.DateField(blank=True, null=True, verbose_name='Assignment 2 date')
    assignment2_grade = models.IntegerField(blank=True, null=True, verbose_name='Assignment 2 grade')
    assignment3_date = models.DateField(blank=True, null=True, verbose_name='Assignment 3 date')
    assignment3_grade = models.IntegerField(blank=True, null=True, verbose_name='Assignment 3 grade')
    journal1_date = models.DateField(blank=True, null=True, verbose_name='Journal 1 date')
    journal2_date = models.DateField(blank=True, null=True, verbose_name='Journal 2 date')
    journal_cats_points = models.IntegerField(blank=True, null=True, verbose_name='Journal CATS points')
    is_introductory_course = models.BooleanField(verbose_name='Introductory course', default=False)

    class Meta:
        db_table = 'certhe_marks'
        verbose_name = 'Certificate of Higher Education marks'
