from django.urls import path, include
from . import views

app_name = 'tutor-payment'

quick_payments_patterns = ([
    path('extras/<int:pk>', views.Extras.as_view(), name='extras'),  # 'tutor-payment:quick:extras'
], 'quick')

urlpatterns = [
    path('quick/', include(quick_payments_patterns)),
]
