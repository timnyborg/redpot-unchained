from django.urls import path

from . import views

app_name = 'cabs_booking'

urlpatterns = [
    path('annual-booking', views.AnnualWeeklyClassBookings.as_view(), name='annual-booking'),
    path('module-booking/<int:pk>', views.CreateModuleBookings.as_view(), name='module-booking'),
]
