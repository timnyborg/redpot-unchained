from django.db import models

from apps.core.models import SignatureModel


class MailingList(models.Model):
    owners = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=512, null=False)
    title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title


class System(models.Model):
    system_name = models.CharField(max_length=50, unique=True, null=False)
    system_email = models.TextField()

    def __str__(self):
        return self.system_name


class Flag(models.Model):
    flag_name = models.CharField(max_length=50, unique=True, null=False)

    def __str__(self):
        return self.flag_name


class Starter(SignatureModel):
    firstname = models.CharField(max_length=50, null=False)
    lastname = models.CharField(max_length=50, null=False)
    email = models.EmailField(
        max_length=50,
        blank=True,
        unique=True,
        help_text="Required if known. If not known, you can update it later. The staff will be flagged for update.",
    )
    job_title = models.CharField(max_length=50, null=False)
    is_active = models.BooleanField(default=True)
    division = models.ForeignKey('core.Division', models.DO_NOTHING, db_column='division', blank=False)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True, verbose_name="End date(if known)")
    is_a_member_of_TSS = models.BooleanField(verbose_name="Is a member of TSS?", blank=True)
    replacing = models.CharField(max_length=50, blank=True)
    telephone = models.CharField(max_length=50, verbose_name="Telephone Ext.", blank=True)
    overseas_calls = models.BooleanField(verbose_name="Overseas call?", blank=True)
    uni_card_number = models.CharField(max_length=50, help_text='Required for an external email routing', blank=True)
    shared_accounts = models.TextField(
        blank=True,
        null=True,
        verbose_name="Shared Mailbox Accounts",
        help_text='Shared mailboxes that need to be accessed. Provide mailbox names.',
    )
    shared_folders = models.TextField(
        blank=True,
        null=True,
        help_text="Network folders that need to be accessed. Provide drive letter and sub-folders.",
    )
    others = models.TextField(blank=True, null=True, help_text="Provide any further information or requests.")
    systems = models.ManyToManyField('System', blank=True)
    mailing_lists = models.ManyToManyField('MailingList', blank=True)
    sso = models.CharField(max_length=50, verbose_name="Uni SSO", blank=True)
    flags = models.ManyToManyField('Flag', blank=True)

    def __str__(self):
        return f'{self.firstname} {self.lastname}'
