from django.db import models
# from apps.programme.models import Division, Qualification, Programme
from apps.core.models import SignatureModel, User

class StaffRole(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'staff_role'

    def __str__(self):
        return self.name

class ProgrammeStaff(SignatureModel):
    programme = models.ForeignKey('programme.Programme', models.DO_NOTHING, db_column='programme')
    staff = models.ForeignKey(User, models.DO_NOTHING, db_column='staff')
    role = models.ForeignKey('StaffRole', models.DO_NOTHING, db_column='role')
    note = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'programme_staff'

