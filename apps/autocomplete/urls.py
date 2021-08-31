from django.urls import path

from . import views

app_name = 'autocomplete'
urlpatterns = [
    path('module', views.ModuleAutocomplete.as_view(), name='module'),
    path('tutor', views.TutorAutocomplete.as_view(), name='tutor'),
    path('enrolment', views.EnrolmentAutocomplete.as_view(), name='enrolment'),
]
