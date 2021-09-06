from django.urls import path

from apps.core.utils.views import not_implemented

from . import views

app_name = 'finance'

urlpatterns = [
    path('add-fees/<int:enrolment_id>', views.AddFees.as_view(), name='add-fees'),
    path('add-module-fees/<int:enrolment_id>', views.AddModuleFees.as_view(), name='add-module-fees'),
    path('add-payment/<int:enrolment_id>', views.AddPayment.as_view(), name='add-payment'),
    path(
        'add-payment/choose-enrolments/<int:student_id>',
        views.MultipleEnrolmentSelection.as_view(),
        name='choose-multiple-enrolments',
    ),
    path('add-payment/pay-enrolments', views.MultipleEnrolmentPayment.as_view(), name='pay-multiple-enrolments'),
    path('transfer/<int:enrolment_id>', views.Transfer.as_view(), name='transfer'),
    path(
        'delete-allocation/<int:allocation>',
        not_implemented,
        name='delete-allocation',
    ),
    path('receipt/<int:allocation>/<int:enrolment_id>', not_implemented, name='receipt'),
]
