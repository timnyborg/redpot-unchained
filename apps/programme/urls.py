from django.urls import path
from django.views.defaults import page_not_found
from . import views

app_name = 'programme'
urlpatterns = [
    path('search', views.Search.as_view(), name='search'),
    path('new', views.New.as_view(), name='new'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('add-module/<int:programme_id>', page_not_found, name='add-module'),
]
