from datetime import datetime

from django.db import models
from django.urls import reverse

# todo: put this into the portfolio table
OFFICES = {
    31: 'Day & Weekend Events Office',
    32: 'Weekly Classes Office',
    17: 'Online Courses Office',
}


class Waitlist(models.Model):
    """A student's spot on a module waitlist"""

    module = models.ForeignKey('module.Module', models.DO_NOTHING, db_column='module', related_name='waitlists')
    student = models.ForeignKey('student.Student', models.DO_NOTHING, db_column='student', related_name='waitlists')
    listed_on = models.DateTimeField(default=datetime.now)
    emailed_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'module_waitlist'

    def get_delete_url(self) -> str:
        return reverse('waitlist:delete', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        return f'{self.student} on {self.module}'
