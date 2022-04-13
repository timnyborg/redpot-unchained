from django.urls import path

from . import views

app_name = 'moodle'

urlpatterns = (
    path('new/<int:student_id>', views.Create.as_view(), name='new'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
    path('assign/<int:module_id>', views.AssignToModule.as_view(), name='assign'),
)
