from django.urls import path

from . import views

app_name = 'amendment'
urlpatterns = [
    path('new/<int:enrolment_id>/<int:type_id>', views.Create.as_view(), name='new'),
]
