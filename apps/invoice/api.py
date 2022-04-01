from datetime import datetime

from rest_framework import authentication, generics, permissions
from rest_framework.views import APIView

from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.core.utils.api_views import OtherModelPermissions

from . import models, serializers, views


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


# --- Website document access - wrapping normal views to allow non-session-based access ---
class InvoicePDF(APIView):
    permissions_required = ['invoice.print_invoice']
    authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
    permission_classes = [OtherModelPermissions]

    get = views.PDF.get


class StatementPDF(APIView):
    permissions_required = ['invoice.print_invoice']
    authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
    permission_classes = [OtherModelPermissions]

    get = views.StatementPDF.get
