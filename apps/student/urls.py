from django.urls import path

from . import views

app_name = 'student'
urlpatterns = [
    path('make-tutor/<int:student_id>', views.MakeTutor.as_view(), name='make-tutor'),
    path('new', views.Create.as_view(), name='new'),
    path('search', views.Search.as_view(), name='search'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('email/create/<int:student_id>', views.CreateEmail.as_view(), name='email-create'),
]
