from django.urls import path

from . import views

app_name = 'banner'

urlpatterns = [path('', views.List.as_view(), name='list')]
