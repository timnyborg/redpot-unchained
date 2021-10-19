from django.urls import path

from . import views

app_name = 'hesa'

urlpatterns = [
    path('', views.ListBatches.as_view(), name='batches'),
    path('batches/', views.ListBatches.as_view(), name='batches'),
    path('new-batch/', views.CreateBatch.as_view(), name='new-batch'),
    path('xml/<int:pk>', views.DownloadXML.as_view(), name='xml'),
]
