from django.urls import path

from . import views

app_name = 'user'
urlpatterns = [
    path('profile', views.EditProfile.as_view(), name='profile'),
    path('edit/<int:pk>', views.EditProfile.as_view(), name='admin-edit'),
    path('new', views.New.as_view(), name='new'),
]
