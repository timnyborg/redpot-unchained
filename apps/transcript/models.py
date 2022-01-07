from django.db import models


class UserRightsSupport(models.Model):
    """A dummy model which allow the creation of rights not tied to any actual model (content_type)"""

    class Meta:
        managed = False  # No database table creation or deletion operations will be performed for this model.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions
        permissions = (
            ('print', 'Can print an individual student transcript'),
            ('batch_print', 'Can produce batches of transcripts'),
        )
