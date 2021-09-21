from django.urls import include, path

from . import views

app_name = 'tutor-payment'

quick_payments_patterns = (
    [
        path('extras/<int:pk>', views.Extras.as_view(), name='extras'),  # 'tutor-payment:quick:extras'
    ],
    'quick',
)

urlpatterns = [
    path('new/<int:tutor_module_id>', views.Create.as_view(), name='new'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
    path('quick/', include(quick_payments_patterns)),
    path('search/', views.Search.as_view(), name='search'),
    path('approve/', views.Approve.as_view(), name='approve'),
]
