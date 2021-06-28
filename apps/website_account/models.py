from django.db import models

from apps.core.models import SignatureModel


class WebsiteAccount(SignatureModel):
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
