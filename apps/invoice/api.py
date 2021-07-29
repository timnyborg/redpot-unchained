from datetime import datetime

from rest_framework import generics, permissions

from django.db import transaction
from django.shortcuts import get_object_or_404

from . import models, serializers


class SaveSchedule(generics.CreateAPIView):
    """
    Replace a payment plan's schedule items
    """

    permission_classes = [permissions.DjangoModelPermissions]
    queryset = models.ScheduledPayment.objects.all()  # for the permissions
    serializer_class = serializers.ScheduledPaymentListSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        plan = get_object_or_404(models.PaymentPlan, pk=self.kwargs['plan_id'])
        plan.scheduled_payments.all().delete()
        serializer.save(
            payment_plan=plan,
            created_by=self.request.user.username,
            created_on=datetime.now(),
            modified_by=self.request.user.username,
            modified_on=datetime.now(),
        )
