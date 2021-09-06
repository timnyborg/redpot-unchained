from django.urls import path

from . import views

app_name = 'staff_forms'
urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('starter', views.StarterFormView.as_view(), name='starter'),
    path('leaver', views.LeaverFormView.as_view(), name='leaver'),
]
