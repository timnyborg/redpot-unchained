from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


@models.CharField.register_lookup
class UnAccent(models.Transform):
    lookup_name = 'unaccent'

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        return '{} COLLATE Latin1_General_CI_AI'.format(lhs), params