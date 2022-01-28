from django.urls import path

from . import views

app_name = 'proposal'

urlpatterns = [
    path('new', views.New.as_view(), name='new'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
    path('search', views.Search.as_view(), name='search'),
]
