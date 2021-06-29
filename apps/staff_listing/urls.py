from django.urls import path
from . import views

app_name = 'staff_listing'
urlpatterns = [
    path('', views.index),
    path('wall', views.WallListView.as_view(), name='wall'),
    path('list', views.StaffListView.as_view(), name='list'),
    path('profile/<int:pk>', views.StaffDetailView.as_view(), name='profile'),
    path('courses', views.courses, name='courses'),
]
