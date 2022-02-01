"""Tools needed to provide backward compatibility with web2py applications while we have a mix of frameworks"""

from __future__ import annotations

from django.db import models


class PipeSeparatedStringsField(models.TextField):
    """A backwards compatibility field for list:string fields"""

    def from_db_value(self, value, *args) -> list[str]:
        if not value:
            return []

        values = value.strip('|').split('|')
        return list(filter(None, values))  # remove ''

    def to_python(self, value) -> list[str]:
        if isinstance(value, list):
            return value

        return self.from_db_value(value)

    def get_prep_value(self, value) -> str:
        value = value or []
        return '|%s|' % '|'.join(value)

    def value_to_string(self, obj) -> str:
        return self.get_prep_value(self.value_from_object(obj))


class PipeSeparatedIntegersField(models.TextField):
    """A backwards compatibility field for list:integer or list:ref fields"""

    def from_db_value(self, value, *args) -> list[int]:
        if not value:
            return []
        values = value.strip('|').split('|')
        values = list(map(int, filter(None, values)))  # remove ''

        return values

    def to_python(self, value) -> list[int]:
        if isinstance(value, list):
            return value
        if isinstance(value, models.QuerySet):  # Handle ModelMultipleChoiceField submissions
            return [obj.pk for obj in value]

        return self.from_db_value(value)

    def get_prep_value(self, value) -> str:
        value = value or []
        return '|%s|' % '|'.join(map(str, value))

    def value_to_string(self, obj) -> str:
        return self.get_prep_value(self.value_from_object(obj))
