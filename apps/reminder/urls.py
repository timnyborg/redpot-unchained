from django.urls import path

from . import views

app_name = 'reminder'

urlpatterns = [
    path('preview/<int:pk>', views.Preview.as_view(), name='preview'),
]
