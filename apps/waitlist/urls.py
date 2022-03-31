from django.urls import path

from . import views

app_name = 'waitlist'

urlpatterns = [
    path('add/<int:student_id>', views.Add.as_view(), name='add'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
    path('email/single/<int:pk>', views.EmailSingle.as_view(), name='email-single'),
    path('email/multiple/<int:module>', views.EmailMultiple.as_view(), name='email-multiple'),
    path('email/multiple/<int:previous_module>/<int:module>', views.EmailMultiple.as_view(), name='email-multiple'),
]
