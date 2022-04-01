from rest_framework import authentication
from rest_framework.views import APIView

from apps.core.utils.api_views import OtherModelPermissions

from . import views


# --- Website document access - wrapping normal views ---
class ReceiptPDF(APIView):
    permissions_required = ['finance.print_receipt']
    # todo: consider replacing basic auth with DRF's token authentication
    authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
    permission_classes = [OtherModelPermissions]

    get = views.ReceiptPDF.get
