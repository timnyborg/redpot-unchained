from django.urls import path

from . import views

app_name = 'marketing'
urlpatterns = [
    path('export', views.ExportXML.as_view(), name='export'),
]
