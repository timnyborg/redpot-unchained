from datetime import datetime

from rest_framework import generics, permissions

from . import models, serializers


class AddressUpdate(generics.UpdateAPIView):
    queryset = models.Address.objects.all()
    serializer_class = serializers.AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer) -> None:
        serializer.save(
            modified_by=self.request.user.username,
            modified_on=datetime.now(),
        )


class EmailUpdate(generics.UpdateAPIView):
    queryset = models.Email.objects.all()
    serializer_class = serializers.EmailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer) -> None:
        serializer.save(
            modified_by=self.request.user.username,
            modified_on=datetime.now(),
        )
