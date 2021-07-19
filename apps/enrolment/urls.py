from django.urls import path

from . import views

app_name = 'enrolment'

urlpatterns = [
    path('new/<int:qa_id>', views.Create.as_view(), name='create'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
]
