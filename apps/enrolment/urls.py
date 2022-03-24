from django.urls import path

from . import views

app_name = 'enrolment'

urlpatterns = [
    path('new/<int:qa_id>', views.Create.as_view(), name='create'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
    path('statement/<int:pk>', views.StatementPDF.as_view(), name='statement'),
    path('confirmation-email/<int:enrolment>', views.ConfirmationEmail.as_view(), name='confirmation-email'),
    path(
        'confirmation-email/invoice/<int:invoice>',
        views.ConfirmationEmail.as_view(),
        name='confirmation-email-by-invoice',
    ),
]
