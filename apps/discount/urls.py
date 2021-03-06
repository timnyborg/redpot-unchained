from django.urls import path

from . import views

app_name = 'discount'

urlpatterns = [
    path('new', views.Create.as_view(), name='new'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
    path('search', views.Search.as_view(), name='search'),
]
