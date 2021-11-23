from __future__ import annotations

from typing import Any

from django import forms

from .. import models


class ApproverChoiceField(forms.ModelChoiceField):
    """
    A form field that allows you to choose a user with a given permission, to be used when selecting approvers, etc.
    """

    def __init__(self, permission: str, *, include_superusers: bool = False, **kwargs):

        defaults: dict[str, Any] = {
            'empty_label': '– Select –',
            'to_field_name': 'username',
        }

        queryset = models.User.objects.with_perm(
            perm=permission,
            backend='django.contrib.auth.backends.ModelBackend',
            include_superusers=include_superusers,
        )
        super().__init__(queryset, **defaults, **kwargs)

    def label_from_instance(self, obj: models.User) -> str:
        return obj.get_full_name()


class SITSLockingFormMixin:
    """ModelForm mixin which automatically disables an instance's SITS fields if required"""

    instance: models.SITSLockingModelMixin
    fields: dict

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.instance.locked_fields.intersection(self.fields):
            self.fields[field].disabled = True
