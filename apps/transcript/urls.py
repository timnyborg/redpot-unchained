from django.urls import path

from . import views

app_name = 'transcript'

urlpatterns = [
    path('undergraduate/<int:student_id>', views.pdf, {'level': 'ug'}, name='undergraduate-pdf'),
    path('postgraduate/<int:student_id>', views.pdf, {'level': 'pg'}, name='postgraduate-pdf'),
]
