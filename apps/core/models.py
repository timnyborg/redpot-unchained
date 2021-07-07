import os
from datetime import datetime

from django_resized import ResizedImageField

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.deconstruct import deconstructible

from .utils.models import PhoneField
from django.urls import reverse


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
    # help ensure on update forms
    created_by = models.CharField(max_length=8, blank=True, null=True, editable=False)
    created_on = models.DateTimeField(blank=True, null=True, default=datetime.now, editable=False)
    modified_by = models.CharField(max_length=8, blank=True, null=True, editable=False)
    modified_on = models.DateTimeField(blank=True, null=True, default=datetime.now, editable=False)

    class Meta:
        abstract = True


@deconstructible
class PathAndRename(object):
    """See https://stackoverflow.com/q/25767787/9461432"""

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # get filename
        filename = f'{instance.username}.{ext}'
        # return the whole path to the file
        return os.path.join(self.path, filename)


rename_profile_image = PathAndRename('images/staff_profile/')


class User(SignatureModel, AbstractUser):
    """Extends the standard django user model with additional fields"""

    default_approver = models.CharField(max_length=32, blank=True, null=True)
    role = models.CharField(max_length=512, blank=True, null=True)
    image = ResizedImageField(upload_to=rename_profile_image, null=True, blank=True)
    phone = PhoneField(max_length=512, blank=True, null=True)
    room = models.CharField(max_length=512, blank=True, null=True)
    on_facewall = models.BooleanField(default=True)
    division = models.ForeignKey('Division', on_delete=models.CASCADE, db_column='division')

    def get_absolute_url(self):
        return reverse('staff_list:profile', args=[self.pk])

    def phone_number(self):
        if self.phone:
            return self.phone.replace('+44 (0)1865 2', '')


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
    manager = models.ForeignKey('core.User', models.DO_NOTHING, db_column='manager', related_name='manager_of', blank=True, null=True)

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
