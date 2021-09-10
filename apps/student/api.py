from rest_framework import generics, permissions

from apps.core.utils.api_views import TimestampMixin

from . import models, serializers


class AddressUpdate(TimestampMixin, generics.UpdateAPIView):
    queryset = models.Address.objects.all()
    serializer_class = serializers.AddressSerializer
    permission_classes = [permissions.IsAuthenticated]


class EmailUpdate(TimestampMixin, generics.UpdateAPIView):
    queryset = models.Email.objects.all()
    serializer_class = serializers.EmailSerializer
    permission_classes = [permissions.IsAuthenticated]


class PhoneUpdate(TimestampMixin, generics.UpdateAPIView):
    queryset = models.Phone.objects.all()
    serializer_class = serializers.PhoneSerializer
    permission_classes = [permissions.IsAuthenticated]
