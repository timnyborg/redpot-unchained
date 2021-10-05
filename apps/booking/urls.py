from django.urls import path

from . import views

app_name = 'booking'

urlpatterns = [
    # accom
    path('accommodation/add/<int:enrolment_id>', views.CreateAccommodation.as_view(), name='add-accommodation'),
    path('accommodation/edit/<int:pk>', views.EditAccommodation.as_view(), name='edit-accommodation'),
    path('accommodation/delete/<int:pk>', views.DeleteAccommodation.as_view(), name='delete-accommodation'),
    # catering
    path('catering/add/<int:enrolment_id>', views.CreateCatering.as_view(), name='add-catering'),
    path('catering/delete/<int:pk>', views.DeleteCatering.as_view(), name='delete-catering'),
]
