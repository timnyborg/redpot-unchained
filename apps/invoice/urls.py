from django.urls import path

from . import views

app_name = 'invoice'
urlpatterns = [
    path('search', views.Search.as_view(), name='search'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('lookup', views.Lookup.as_view(), name='lookup'),
    path('choose-enrolments/<int:student_id>', views.ChooseEnrolments.as_view(), name='choose-enrolments'),
    path('choose-fees/<int:student_id>', views.ChooseFees.as_view(), name='choose-fees'),
    path('create/<int:student_id>', views.Create.as_view(), name='create'),
    path('upload-rcp', views.UploadRCP.as_view(), name='upload-rcp'),
]
