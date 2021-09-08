from datetime import datetime

from rest_framework import serializers

from django import http


class TimestampMixin:
    """Mixin to automatically update timestamp fields on an APIView"""

    request: http.HttpRequest

    def perform_update(self, serializer: serializers.Serializer) -> None:
        serializer.save(
            modified_by=self.request.user.username,
            modified_on=datetime.now(),
        )
