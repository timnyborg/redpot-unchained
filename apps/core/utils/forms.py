from django import forms

from .. import models


class ApproverChoiceField(forms.ModelChoiceField):
    """
    A form field that allows you to choose a user with a given permission, to be used when selecting approvers, etc.
    """

    def __init__(self, permission: str, *, include_superusers: bool = False, **kwargs):
        defaults = {
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
