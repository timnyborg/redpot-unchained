from django.urls import path

from . import views

app_name = 'module'
urlpatterns = [
    path('search', views.Search.as_view(), name='search'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
]
