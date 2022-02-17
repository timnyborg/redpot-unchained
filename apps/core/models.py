from __future__ import annotations

from datetime import datetime
from pathlib import Path

from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFit

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from .utils import postal
from .utils.models import PhoneField


class SignatureModel(models.Model):
    """Common definition of our signature fields, for easy inclusion
    The _on fields are populated when the record is created, and modified_on must be managed manually on updates
    The _by fields must be managed manually on inserts & updates

    This can be done in the view's form_valid():
    UpdateView:
        def form_valid(self, form):
            form.instance.modified_on = datetime.now()
            form.instance.modified_by = self.request.user.username
            return super().form_valid(form)

    CreateView:
        def form_valid(self, form):
            form.instance.created_by = self.request.user.username # Only for CreateViews
            form.instance.modified_on = datetime.now()
            form.instance.modified_by = self.request.user.username
            return super().form_valid(form)

    This work is done by utils.views.AutoTimestampMixin
    We could also turn it into a Form mixin.  Not sure which is preferable
    """

    # Todo: consider making these non-nullable.  Would ensure timestamps are applied to all create forms, but wouldn't
    #  help ensure on update forms
    created_by = models.CharField(max_length=150, blank=True, null=True, editable=False)
    created_on = models.DateTimeField(blank=True, null=True, default=datetime.now, editable=False)
    modified_by = models.CharField(max_length=150, blank=True, null=True, editable=False)
    modified_on = models.DateTimeField(blank=True, null=True, default=datetime.now, editable=False)

    class Meta:
        abstract = True


class AddressModel(models.Model):
    """A set of shared field definitions for models storing address data"""

    line1 = models.CharField(max_length=128, blank=True, null=True, verbose_name='Address line 1')
    line2 = models.CharField(max_length=128, blank=True, null=True, verbose_name='Line 2')
    line3 = models.CharField(max_length=128, blank=True, null=True, verbose_name='Line 3')
    town = models.CharField(max_length=64, blank=True, null=True, verbose_name='City/town')
    countystate = models.CharField(max_length=64, blank=True, null=True, verbose_name='County/state')
    country = models.CharField(max_length=64, blank=True, null=True)
    postcode = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        abstract = True

    def get_formatted(self) -> str:
        """Produced a formatted version of the address"""
        return postal.FormattedAddress(self).as_string()


class SITSLockingModelMixin:
    """Adds functionality for determining which instances and which fields are sits-managed"""

    sits_managed_fields: list = []

    @property
    def is_sits_record(self) -> bool:
        """Determine whether the object originates in SITS.  Must be overridden"""
        raise NotImplementedError(f'{self.__class__.__name__} must implement an is_sits_record method')

    @property
    def locked_fields(self) -> set[str]:
        """List which fields are locked for editing

        Useful in model forms, which can dynamically lock fields using SITSLockingFormMixin
        """
        return set(self.sits_managed_fields) if self.is_sits_record else set()


def get_profile_image_filename(instance: 'User', filename: str) -> str:
    ext = Path(filename).suffix
    filename = f'{instance.username}{ext}'
    return f'images/staff/{filename}'


class User(SignatureModel, AbstractUser):
    """Extends the standard django user model with additional fields"""

    default_approver = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        related_name='+',
        to_field='username',
        db_column='default_approver',
        blank=True,
        null=True,
    )
    role = models.CharField(max_length=512, blank=True, null=True)
    image = ProcessedImageField(
        upload_to=get_profile_image_filename,
        null=True,
        blank=True,
        processors=[ResizeToFit(1000, 1000)],
        format='JPEG',
        options={'quality': 70},
    )
    phone = PhoneField(max_length=512, blank=True, null=True)
    room = models.CharField(max_length=512, blank=True, null=True)
    on_facewall = models.BooleanField(default=True)
    division = models.ForeignKey('Division', on_delete=models.CASCADE, db_column='division', default=1)

    def get_absolute_url(self) -> str:
        return reverse('staff_list:profile', args=[self.pk])

    def get_edit_url(self) -> str:
        return reverse('user:edit', args=[self.pk])

    def phone_number(self):
        if self.phone:
            return self.phone.replace('+44 (0)1865 2', '')


class UserRightsSupport(models.Model):
    """A dummy model which allow the creation of rights not tied to any actual model (content_type)"""

    class Meta:
        managed = False  # No database table creation or deletion operations will be performed for this model.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions
        permissions = (
            # Blanket team-level permissions, replicating what existed in w2p, handling rights which don't map
            # onto a model.  They violate RBAM and couple the codebase to the organization, so avoid using these.
            # Instead, implement narrower rights that can be given to a group.  # todo: phase out use
            ('finance', 'Generic finance-team rights'),
            ('marketing', 'Generic marketing-team rights'),
        )


class Portfolio(models.Model):
    name = models.CharField(max_length=128)
    division = models.ForeignKey('Division', models.DO_NOTHING, db_column='division')
    email = models.EmailField(max_length=256, blank=True, null=True)
    phone = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'portfolio'
        ordering = ['name']

    def __str__(self):
        return self.name


class Division(models.Model):
    name = models.CharField(max_length=64)
    shortname = models.CharField(max_length=8, blank=True, null=True)
    email = models.EmailField(max_length=256, blank=True, null=True)
    finance_prefix = models.CharField(max_length=2, blank=True, null=True)
    manager = models.ForeignKey(
        'core.User', models.DO_NOTHING, db_column='manager', related_name='manager_of', blank=True, null=True
    )

    class Meta:
        db_table = 'division'
        ordering = ['name']

    def __str__(self):
        return self.name


@models.CharField.register_lookup
class UnAccent(models.Transform):
    """A transform that allows us to do accent-insensitive text searching in MSSQL
    Allows filters like Modelname.objects.filter(title__unaccent__startswith='Joao')
    """

    lookup_name = 'unaccent'

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        return '{} COLLATE Latin1_General_CI_AI'.format(lhs), params


@models.CharField.register_lookup
class Like(models.Lookup):
    """Allows us to do lookups with MSSQL's LIKE wildcards, like Modelname.objects.filter(code__like='O18%p%')"""

    lookup_name = 'like'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s LIKE %s' % (lhs, rhs), params
