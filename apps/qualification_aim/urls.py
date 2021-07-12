from django.urls import path

from . import views

app_name = 'qualification_aim'
urlpatterns = [
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('new/<int:student_id>', views.Create.as_view(), name='new'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('certhe-marks/<int:qa_id>', views.EditCertHEMarks.as_view(), name='certhe-marks'),
]
