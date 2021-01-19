from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


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
    created_by = models.CharField(max_length=8, blank=True, null=True, )
    created_on = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified_by = models.CharField(max_length=8, blank=True, null=True)
    modified_on = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        abstract = True


@models.CharField.register_lookup
class UnAccent(models.Transform):
    """A transform that allows us to do accent-insensitive text searching in MSSQL
       Allows filters like Modelname.objects.filter(title__unaccent__startswith='Joao')
    """
    lookup_name = 'unaccent'

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        return '{} COLLATE Latin1_General_CI_AI'.format(lhs), params