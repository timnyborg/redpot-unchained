from django.urls import path

from . import views

app_name = 'application'
urlpatterns = [
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('enrol-student/<int:pk>', views.CreateAndEnrolStudent.as_view(), name='enrol-student'),
]
