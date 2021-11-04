from django.urls import include, path

from apps.core.utils.views import not_implemented

from . import api, views

app_name = 'student'

address_urls = (
    [
        path('new/<int:student_id>', views.CreateAddress.as_view(), name='new'),
        path('edit/<int:pk>', views.EditAddress.as_view(), name='edit'),
        path('delete/<int:pk>', views.DeleteAddress.as_view(), name='delete'),
    ],
    'address',
)

email_urls = (
    [
        path('new/<int:student_id>', views.CreateEmail.as_view(), name='new'),
        path('edit/<int:pk>', views.EditEmail.as_view(), name='edit'),
        path('delete/<int:pk>', views.DeleteEmail.as_view(), name='delete'),
    ],
    'email',
)

phone_urls = (
    [
        path('new/<int:student_id>', views.CreatePhone.as_view(), name='new'),
        path('edit/<int:pk>', views.EditPhone.as_view(), name='edit'),
        path('delete/<int:pk>', views.DeletePhone.as_view(), name='delete'),
    ],
    'phone',
)

other_id_urls = (
    [
        path('new/<int:student_id>', views.CreateOtherID.as_view(), name='new'),
        path('edit/<int:pk>', views.EditOtherID.as_view(), name='edit'),
        path('delete/<int:pk>', views.DeleteOtherID.as_view(), name='delete'),
    ],
    'other-id',
)

moodle_id_urls = (
    [
        path('new/<int:student_id>', views.CreateMoodleID.as_view(), name='new'),
        path('edit/<int:pk>', views.EditMoodleID.as_view(), name='edit'),
        path('delete/<int:pk>', views.DeleteMoodleID.as_view(), name='delete'),
    ],
    'moodle-id',
)

emergency_email_urls = (
    [
        path('edit/<int:student_id>', views.CreateOrEditEmergencyContact.as_view(), name='edit'),
        path('delete/<int:pk>', views.DeleteEmergencyContact.as_view(), name='delete'),
    ],
    'emergency-contact',
)

enquiry_urls = ([path('delete/<int:pk>', views.DeleteEnquiry.as_view(), name='delete')], 'enquiry')

urlpatterns = [
    path('make-tutor/<int:student_id>', views.MakeTutor.as_view(), name='make-tutor'),
    path('new', views.Create.as_view(), name='new'),
    path('search', views.Search.as_view(), name='search'),
    path('lookup', views.Lookup.as_view(), name='lookup'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('statement/<int:pk>', views.StatementPDF.as_view(), name='statement'),
    path('email/', include(email_urls)),
    path('phone/', include(phone_urls)),
    path('other-id/', include(other_id_urls)),
    path('moodle-id/', include(moodle_id_urls)),
    path('enquiry/', include(enquiry_urls)),
    path('edit-diet/<int:student_id>', views.CreateOrEditDiet.as_view(), name='edit-diet'),
    path('emergency-contact/', include(emergency_email_urls)),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
    path('address/', include(address_urls)),
    path('merge/', not_implemented, name='merge'),
    # apis
    path('api/update-address/<int:pk>', api.AddressUpdate.as_view(), name='address-api'),
    path('api/update-email/<int:pk>', api.EmailUpdate.as_view(), name='email-api'),
    path('api/update-phone/<int:pk>', api.PhoneUpdate.as_view(), name='phone-api'),
]
