from django.urls import path

from . import views

app_name = 'transcript'

urlpatterns = [
    path('status/<uuid:task_id>', views.Status.as_view(), name='status'),
    path('progress/<uuid:task_id>', views.ViewProgress.as_view(), name='progress'),
]
