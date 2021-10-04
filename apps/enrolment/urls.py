from django.urls import path

from . import views

app_name = 'enrolment'

urlpatterns = [
    path('new/<int:qa_id>', views.Create.as_view(), name='create'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
    path('add-catering/<int:enrolment_id>', views.CreateCatering.as_view(), name='add-catering'),
    path('delete-catering/<int:pk>', views.DeleteCatering.as_view(), name='delete-catering'),
]
