from django.urls import path

from . import views

app_name = 'autocomplete'
urlpatterns = [
    path('module', views.ModuleAutocomplete.as_view(), name='module'),
    path('tutor', views.TutorAutocomplete.as_view(), name='tutor'),
    path('enrolment', views.EnrolmentAutocomplete.as_view(), name='enrolment'),
    path('rtw', views.RtwAutocomplete.as_view(), name='rtw'),
    path('user', views.UserAutocomplete.as_view(), name='user'),
    path('tutor-on-module', views.TutorModuleAutocomplete.as_view(), name='tutor-on-module'),
]
