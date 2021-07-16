from django.urls import path

from . import views

app_name = 'finance'

urlpatterns = [
    path('add-fees/<int:enrolment_id>', views.AddFees.as_view(), name='add-fees'),
    path('add-module-fees/<int:enrolment_id>', views.AddModuleFees.as_view(), name='add-module-fees'),
    path('add-payment/<int:enrolment_id>', views.AddPayment.as_view(), name='add-payment'),
]
