from datetime import datetime

from rest_framework import permissions, serializers

from django import http


class TimestampMixin:
    """Mixin to automatically update timestamp fields on an APIView"""

    request: http.HttpRequest

    def perform_update(self, serializer: serializers.Serializer) -> None:
        serializer.save(
            modified_by=self.request.user.username,
            modified_on=datetime.now(),
        )


class OtherModelPermissions(permissions.BasePermission):
    """Allows an APIView to require custom model permissions, e.g. 'contract.approve_contract'"""

    def has_permission(self, request, view) -> bool:
        if not hasattr(view, 'permissions_required'):
            raise ValueError('The APIView must have a `permissions_required` attribute')
        return request.user.has_perms(view.permissions_required)
