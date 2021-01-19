from django.urls import path
from django.views.defaults import page_not_found
from . import views


app_name = 'invoice'
urlpatterns = [
    path('search', views.Search.as_view(), name='search'),
    path('view/<int:pk>', page_not_found, name='view'),
]
