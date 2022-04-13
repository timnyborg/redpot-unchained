from django.db import models
from django.urls import reverse

from apps.core.models import SignatureModel


class MoodleID(SignatureModel):
    moodle_id = models.IntegerField(
        unique=True, error_messages={'unique': 'Moodle ID already in use'}, verbose_name='Moodle ID'
    )  # todo: rename this field
    student = models.OneToOneField('student.Student', models.DO_NOTHING, db_column='student', related_name='moodle_id')
    first_module_code = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        db_table = 'moodle_id'
        verbose_name = 'Moodle ID'

    def get_absolute_url(self) -> str:
        return self.student.get_absolute_url() + '#other_ids'

    def get_edit_url(self) -> str:
        return reverse('moodle:edit', kwargs={'pk': self.pk})

    def get_delete_url(self) -> str:
        return reverse('moodle:delete', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        return str(self.moodle_id)
