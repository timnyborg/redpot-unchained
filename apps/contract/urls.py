from django.urls import path

from . import views

app_name = 'contract'
urlpatterns = [
    path('new/<int:tutor_module_id>/<str:type>', views.Create.as_view(), name='new'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('pdf/<int:pk>', views.PDF.as_view(), name='pdf'),
]
