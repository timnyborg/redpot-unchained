from rest_framework import serializers

from . import models


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Module
        fields = ('auto_publish', 'auto_reminder', 'auto_feedback', 'status', 'is_published')

    def update(self, instance, validated_data) -> models.Module:
        instance = super().update(instance, validated_data)
        # Enabling auto-publishing may entail a status change.  Todo: Should this be on the model?
        if validated_data.get('auto_publish'):
            instance.update_status()
        return instance

    def validate_is_published(self, value: bool) -> bool:
        if value and not self.instance.is_publishable:
            raise serializers.ValidationError('Module cannot be published', code='unpublishable')
        return value
