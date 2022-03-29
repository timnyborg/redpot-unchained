from django.urls import path

from . import views

app_name = 'website_basket'
urlpatterns = [
    path('push-payment', views.PushPayment.as_view(), name='push-payment'),
]
