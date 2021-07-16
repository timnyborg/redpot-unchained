from django.urls import path

from . import views

app_name = 'enrolment'

urlpatterns = [
    path('view/<int:pk>', views.View.as_view(), name='view'),
]
