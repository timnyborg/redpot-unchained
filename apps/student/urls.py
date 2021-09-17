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

urlpatterns = [
    path('make-tutor/<int:student_id>', views.MakeTutor.as_view(), name='make-tutor'),
    path('new', views.Create.as_view(), name='new'),
    path('search', views.Search.as_view(), name='search'),
    path('lookup', views.Lookup.as_view(), name='lookup'),
    path('edit/<int:pk>', views.Edit.as_view(), name='edit'),
    path('view/<int:pk>', views.View.as_view(), name='view'),
    path('delete/<int:pk>', views.Delete.as_view(), name='delete'),
    path('email/create/<int:student_id>', views.CreateEmail.as_view(), name='email-create'),
    path('address/', include(address_urls)),
    path('merge/', not_implemented, name='merge'),
    # apis
    path('api/update-address/<int:pk>', api.AddressUpdate.as_view(), name='address-api'),
    path('api/update-email/<int:pk>', api.EmailUpdate.as_view(), name='email-api'),
    path('api/update-phone/<int:pk>', api.PhoneUpdate.as_view(), name='phone-api'),
]
