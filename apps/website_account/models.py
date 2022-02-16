from datetime import datetime
from typing import Optional

from django.db import models
from django.utils.functional import cached_property

from apps.core.models import SignatureModel


class WebsiteAccount(SignatureModel):
    """Legacy web2py accounts"""

    student = models.ForeignKey(
        'student.Student',
        models.DO_NOTHING,
        db_column='student',
        related_name='website_accounts',
        related_query_name='website_account',
    )
    username = models.EmailField(
        max_length=256,
        unique=True,
        help_text='This must be a valid email address',
        error_messages={'unique': 'This username is already in use'},
    )
    password = models.CharField(
        max_length=256, blank=True, help_text='This is an encrypted value, not the actual password'
    )
    is_disabled = models.BooleanField(default=False, verbose_name='Disabled?')
    reset_password_key = models.CharField(max_length=512, blank=True, null=True, editable=False)

    class Meta:
        db_table = 'login'
        permissions = [('edit_password', 'Can edit website account passwords')]

    def __str__(self) -> str:
        return str(self.username)

    @cached_property
    def last_login(self) -> Optional[datetime]:
        """Returns the max value of field time_stamp from WebsiteAccountEvent with Logged-in description
        If null then take login created on date"""

        return (
            WebsiteAccountEvent.objects.filter(user_id=self.id, description__contains='Logged-in').aggregate(
                last=models.Max('time_stamp')
            )['last']
        ) or self.created_on

    def get_history(self) -> models.QuerySet['WebsiteAccountEvent']:
        """Returns a queryset of auth event records attached to the account
        Doesn't rely on user_id, which is oddly null for password resets
        """
        return WebsiteAccountEvent.objects.filter(description__contains=self.pk)


class WebsiteAccountEvent(models.Model):
    """Record of logins, logouts, password change requests"""

    time_stamp = models.DateTimeField(blank=True, null=True)
    client_ip = models.CharField(max_length=512, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    origin = models.CharField(max_length=512, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'public_auth_event'
