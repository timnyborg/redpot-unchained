from django.urls import path

from . import views

app_name = 'hesa_data_futures'

urlpatterns = [
    path('', views.List.as_view()),
    path('batches/', views.List.as_view(), name='list'),
    path('batch/<int:pk>', views.View.as_view(), name='view'),
    path('batch/<int:pk>/<str:model_name>', views.View.as_view(), name='view'),
    path('new-batch/', views.Create.as_view(), name='new-batch'),
    path('build-xml/<int:pk>', views.BuildXML.as_view(), name='build-xml'),
    path('delete-batch/<int:pk>', views.Delete.as_view(), name='delete-batch'),
    path('xml/<int:pk>', views.DownloadXML.as_view(), name='download-xml'),
]
