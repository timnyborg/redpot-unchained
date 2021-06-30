from django.urls import path

from . import views

app_name = 'module'

urlpatterns = [
    path('clone/<int:pk>', views.Clone.as_view(), name='clone'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('new', views.New.as_view(), name='new'),
    path('search', views.Search.as_view(), name='search'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('add-programme/<int:module_id>', views.AddProgramme.as_view(), name='add-programme'),
    # support functions
    path('toggle-auto-reminder/<int:pk>', views.toggle_auto_reminder, name='toggle-auto-reminder'),
    path('toggle-auto-feedback/<int:pk>', views.toggle_auto_feedback, name='toggle-auto-feedback'),
    # reports
    path('student-list/<int:pk>', views.StudentList.as_view(), name='student-list'),
    path('moodle-list/<int:pk>', views.MoodleList.as_view(), name='moodle-list'),
]
