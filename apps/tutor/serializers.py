from rest_framework import serializers

from . import models


class TutorModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TutorModule
        fields = ('display_order',)
