from django.urls import path

from . import views

app_name = 'website_account'
urlpatterns = [
    path('new/<int:student_id>', views.Create.as_view(), name='create'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
]
