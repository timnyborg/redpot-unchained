from django.db import models
from apps.core.models import SignatureModel, User, Division
from apps.programme.models import Programme

class StaffRole(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'staff_role'

    def __str__(self):
        return self.name

class ProgrammeStaff(SignatureModel):
    programme = models.ForeignKey('programme.Programme', models.CASCADE, db_column='programme', related_name='programme_staff_set')
    staff = models.ForeignKey(User, models.CASCADE, db_column='staff', related_name='programme_staff_set')
    role = models.ForeignKey('StaffRole', models.CASCADE, db_column='role')
    note = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'programme_staff'

