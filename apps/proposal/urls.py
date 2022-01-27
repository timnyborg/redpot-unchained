from django.urls import path

from . import views

app_name = 'proposal'

urlpatterns = [
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
]
