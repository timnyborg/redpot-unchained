from rest_framework import serializers

from . import models


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = ('is_default', 'is_billing')


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Email
        fields = ('is_default',)
