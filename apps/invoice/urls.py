from django.urls import path

from . import api, views

app_name = 'invoice'
urlpatterns = [
    path('search', views.Search.as_view(), name='search'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('lookup', views.Lookup.as_view(), name='lookup'),
    path('upload-rcp', views.UploadRCP.as_view(), name='upload-rcp'),
    path('credit/<int:pk>', views.Credit.as_view(), name='credit'),
    path('payment/select/<int:student_id>', views.SelectForPayment.as_view(), name='select-for-payment'),
    path('payment/<int:pk>', views.Payment.as_view(), name='payment'),
    path('pdf/<int:pk>', views.PDF.as_view(), name='pdf'),
    path('statement/<int:pk>', views.StatementPDF.as_view(), name='statement'),
    # invoice creation steps
    path('choose-enrolments/<int:student_id>', views.ChooseEnrolments.as_view(), name='choose-enrolments'),
    path('choose-fees/<int:student_id>', views.ChooseFees.as_view(), name='choose-fees'),
    path('create/<int:student_id>', views.Create.as_view(), name='create'),
    # payment plan urls
    path('create-payment-plan/<int:invoice_id>', views.CreatePaymentPlan.as_view(), name='create-payment-plan'),
    path('edit-payment-plan/<int:pk>', views.EditPaymentPlan.as_view(), name='edit-payment-plan'),
    path('edit-payment-schedule/<int:pk>', views.EditSchedule.as_view(), name='edit-payment-schedule'),
    path('save-payment-schedule/<int:plan_id>', api.SaveSchedule.as_view(), name='save-payment-schedule'),
]
