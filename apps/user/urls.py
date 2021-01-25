from django.urls import path
from django.views.defaults import page_not_found
from . import views


app_name = 'user'
urlpatterns = [
    path('profile', views.EditProfile.as_view(), name='profile'),
]
