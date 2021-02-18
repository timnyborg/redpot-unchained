from django.db import models
from django.urls import reverse
from apps.core.models import SignatureModel


class Student(SignatureModel):
    husid = models.BigIntegerField(blank=True, null=True)
    surname = models.CharField(max_length=40)
    firstname = models.CharField(max_length=40)
    title = models.CharField(max_length=20, blank=True, null=True)
    middlename = models.CharField(max_length=40, blank=True, null=True)
    nickname = models.CharField(max_length=64, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    domicile = models.IntegerField(blank=True, null=True)
    nationality = models.IntegerField(blank=True, null=True)
    ethnicity = models.IntegerField(blank=True, null=True)
    religion_or_belief = models.IntegerField(default=99)
    disability = models.IntegerField(blank=True, null=True)
    occupation = models.CharField(max_length=128, blank=True, null=True)
    termtime_postcode = models.CharField(max_length=32, blank=True, null=True)
    note = models.CharField(max_length=1024, blank=True, null=True)
    no_publicity = models.BooleanField(blank=True, null=True)
    is_flagged = models.BooleanField(default=False)
    is_eu = models.BooleanField(blank=True, null=True)
    created_by = models.CharField(max_length=16, blank=True, null=True)
    created_on = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=16, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True)
    deceased = models.BooleanField(db_column='Deceased', blank=True, null=True)  # Field name made lowercase.
    disability_detail = models.CharField(max_length=2048, blank=True, null=True)
    disability_action = models.CharField(max_length=256, blank=True, null=True)
    dars_optout = models.BooleanField(default=True)
    termtime_accommodation = models.IntegerField(blank=True, null=True)
    sits_id = models.IntegerField(blank=True, null=True)
    full_name = models.CharField(max_length=82, blank=True, null=True)
    highest_qualification = models.CharField(max_length=128, blank=True, null=True)
    mail_optin = models.BooleanField(default=False)
    mail_optin_on = models.DateTimeField(blank=True, null=True)
    mail_optin_method = models.CharField(max_length=64, blank=True, null=True)
    email_optin = models.BooleanField(default=False)
    email_optin_method = models.CharField(max_length=64, blank=True, null=True)
    email_optin_on = models.DateTimeField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'student'

    def __str__(self):
        return f'{self.firstname} {self.surname}'

    def get_absolute_url(self):
        return reverse('student-view', args=[self.id])
