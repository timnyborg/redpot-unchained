from django.urls import path

from . import api, views

app_name = 'module'

urlpatterns = [
    path('assign-moodle-ids/<int:module_id>', views.AssignMoodleIDs.as_view(), name='assign-moodle-ids'),
    path('clone/<int:pk>', views.Clone.as_view(), name='clone'),
    path('clone', views.Clone.as_view(), name='clone'),
    path('copy-fees/<int:module_id>', views.CopyFees.as_view(), name='copy-fees'),
    path('copy-web-fields/<int:module_id>', views.CopyWebFields.as_view(), name='copy-web-fields'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('new', views.New.as_view(), name='new'),
    path('search', views.Search.as_view(), name='search'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('add-programme/<int:module_id>', views.AddProgramme.as_view(), name='add-programme'),
    path('edit-hesa-subjects/<int:pk>', views.EditHESASubjects.as_view(), name='edit-hesa-subjects'),
    # reports
    path('student-list/<int:pk>', views.StudentList.as_view(), name='student-list'),
    path('moodle-list/<int:pk>', views.MoodleList.as_view(), name='moodle-list'),
    # apis
    path('update-api/<int:pk>', api.ModuleUpdateAPI.as_view(), name='update-api'),
]
