from rest_framework import serializers

from . import models


class ScheduledPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ScheduledPayment
        fields = ('due_date', 'amount', 'is_deposit')


class ScheduledPaymentListSerializer(serializers.ListSerializer):
    child = ScheduledPaymentSerializer()
