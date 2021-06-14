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
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('new/<int:tutor_module_id>', views.Create.as_view(), name='new'),
    path('quick/', include(quick_payments_patterns)),
    path('search/', views.Search.as_view(), name='search'),
]
