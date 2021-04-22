from django.urls import path

from . import views

app_name = 'student'
urlpatterns = [
    path('search', views.Search.as_view(), name='search'),
    path('email/create/<int:student_id>', views.CreateEmail.as_view(), name='email-create'),
    path('searchStudent', views.searchStudent, name='searchStudent')
]
