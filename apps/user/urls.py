from django.urls import path

from . import views

app_name = 'user'
urlpatterns = [
    path('edit', views.EditProfile.as_view(), name='edit'),
    path('edit/<int:pk>', views.EditProfile.as_view(), name='edit'),
    path('new', views.New.as_view(), name='new'),
]
