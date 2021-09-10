from django.urls import path

from . import views

app_name = 'transcript'

urlpatterns = [
    path('undergraduate/<int:student_id>', views.PDF.as_view(), {'level': 'undergraduate'}, name='undergraduate-pdf'),
    path('postgraduate/<int:student_id>', views.PDF.as_view(), {'level': 'postgraduate'}, name='postgraduate-pdf'),
]
