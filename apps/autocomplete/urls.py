from django.urls import path
from . import views

app_name = 'autocomplete'
urlpatterns = [
    path('module', views.ModuleAutocomplete.as_view(), name='module'),
]
