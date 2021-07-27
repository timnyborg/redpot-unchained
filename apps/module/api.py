from rest_framework import generics, permissions

from . import models, serializers


class ModuleUpdateAPI(generics.UpdateAPIView):
    queryset = models.Module.objects.all()
    serializer_class = serializers.ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
