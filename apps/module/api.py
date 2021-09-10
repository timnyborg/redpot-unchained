from rest_framework import generics, permissions

from apps.core.utils.api_views import TimestampMixin

from . import models, serializers


class ModuleUpdateAPI(TimestampMixin, generics.UpdateAPIView):
    queryset = models.Module.objects.all()
    serializer_class = serializers.ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
