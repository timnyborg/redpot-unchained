from django.urls import path

from . import views

app_name = 'fee'

urlpatterns = [
    path('new/<int:module_id>', views.Create.as_view(), name='new'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
]
