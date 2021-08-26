from django.urls import path

from . import views

app_name = 'amendment'
urlpatterns = [
    path('new/<int:enrolment_id>/<int:type_id>', views.Create.as_view(), name='new'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
    path('approve', views.Approve.as_view(), name='approve'),
]
