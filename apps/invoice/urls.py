from django.urls import path

from . import views

app_name = 'invoice'
urlpatterns = [
    path('search', views.Search.as_view(), name='search'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('lookup', views.Lookup.as_view(), name='lookup'),
]
