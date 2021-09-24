from django.urls import path

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
    path('delete-transaction/<int:allocation>', views.DeleteTransaction.as_view(), name='delete-transaction'),
    path('receipt/<int:allocation>/<int:enrolment_id>', views.ReceiptPDF.as_view(), name='receipt'),
    # Financial batch views
    path('all-batches', views.AllBatches.as_view(), name='all-batches'),
    path('my-batches', views.MyBatches.as_view(), name='my-batches'),
    path('create-batch/<int:type_id>/<str:created_by>', views.CreateBatch.as_view(), name='create-batch'),
    path('print-batch/<int:batch>', views.PrintBatch.as_view(), name='print-batch'),
]
