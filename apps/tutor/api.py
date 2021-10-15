from rest_framework import permissions, response, views

from django.db import transaction

from . import models, serializers


class ReorderAPI(views.APIView):
    """Reorder a set of tutor module records (from their position in an array)"""

    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def patch(self, request, *args, **kwargs) -> response.Response:
        id_list = request.data['ids']
        instances = []
        for idx, obj_id in enumerate(id_list):
            obj = models.TutorModule.objects.get(pk=obj_id)
            obj.display_order = idx
            obj.save()
            instances.append(obj)
        serializer = serializers.TutorModuleSerializer(instances, many=True)
        return response.Response(serializer.data)
