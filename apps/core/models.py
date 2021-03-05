import os

from django.db import models
from django.forms.widgets import TextInput
from django.contrib.auth.models import AbstractUser
from django_resized import ResizedImageField
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible


class PhoneInput(TextInput):
    input_type = 'tel'


class PhoneField(models.CharField):
    default_validators = [RegexValidator(regex='^[-0-9 +()]+$', message='Invalid phone number')]
    widget = PhoneInput


class SignatureModel(models.Model):
    """ Common definition of our signature fields, for easy inclusion
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

        We could turn that into a form mixin, which does one of the behaviours based on class
    """
    created_by = models.CharField(max_length=8, blank=True, null=True, editable=False)
    created_on = models.DateTimeField(blank=True, null=True, auto_now_add=True, editable=False)
    modified_by = models.CharField(max_length=8, blank=True, null=True, editable=False)
    modified_on = models.DateTimeField(blank=True, null=True, auto_now_add=True, editable=False)

    class Meta:
        abstract = True


@deconstructible
class PathAndRename(object):
    """See https://stackoverflow.com/questions/25767787/django-cannot-create-migrations-for-imagefield-with-dynamic-upload-to-value"""

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
