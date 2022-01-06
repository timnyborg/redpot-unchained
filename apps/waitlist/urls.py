from django.urls import path

from . import views

app_name = 'waitlist'

urlpatterns = [
    path('add/<int:student_id>', views.Add.as_view(), name='add'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
]
