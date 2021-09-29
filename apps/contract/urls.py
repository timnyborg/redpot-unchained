from django.urls import path

from . import views

app_name = 'contract'
urlpatterns = [
    path('select/<int:tutor_module_id>', views.Select.as_view(), name='select'),
    path('new/<int:tutor_module_id>/<str:type>', views.Create.as_view(), name='new'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
    path('pdf/<int:pk>', views.PDF.as_view(), name='pdf'),
    path('approve', views.Approve.as_view(), name='approve'),
    path('sign', views.Sign.as_view(), name='sign'),
    # Endpoints
    path('set-status/<int:pk>/<int:status>', views.SetStatus.as_view(), name='set-status'),
    path('mark-returned/<int:pk>', views.MarkReturned.as_view(), name='mark-returned'),
]
