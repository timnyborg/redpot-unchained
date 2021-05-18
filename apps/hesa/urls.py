from django.urls import path

from . import views

app_name = 'hesa'

urlpatterns = [
    path('', views.ListBatches.as_view(), name='batches'),
    path('batches/', views.ListBatches.as_view(), name='batches'),
    path('new-batch/', views.CreateBatch.as_view(), name='new-batch'),
    path('status/<uuid:task_id>/', views.TaskStatus.as_view(), name='status'),
]
