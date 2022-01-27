from django.urls import path

from apps.core.utils.views import not_implemented

from . import views

app_name = 'proposal'

urlpatterns = [
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
    path('search', not_implemented, name='search'),
]
