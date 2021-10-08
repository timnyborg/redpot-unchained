from django.urls import path

from . import views

app_name = 'transcript'

urlpatterns = [
    path(
        'undergraduate/<int:student_id>',
        views.PDF.as_view(),
        {'level': 'undergraduate'},
        name='undergraduate',
    ),
    path(
        'undergraduate/<int:student_id>/headed',
        views.PDF.as_view(),
        {'level': 'undergraduate', 'header': True},
        name='undergraduate-headed',
    ),
    path(
        'postgraduate/<int:student_id>',
        views.PDF.as_view(),
        {'level': 'postgraduate'},
        name='postgraduate',
    ),
    path(
        'postgraduate/<int:student_id>/headed',
        views.PDF.as_view(),
        {'level': 'postgraduate', 'header': True},
        name='postgraduate-headed',
    ),
    path('create-batch', views.CreateBatch.as_view(), name='create-batch'),
    path('view-batch/<str:filename>', views.ViewBatch.as_view(), name='view-batch'),
]
