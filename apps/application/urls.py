from django.urls import path

from apps.core.utils.views import not_implemented

from . import views

app_name = 'application'
urlpatterns = [
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('create-student/<int:pk>', not_implemented, name='create-student'),
]
