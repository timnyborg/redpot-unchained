"""redpot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.defaults import page_not_found
from django.views.generic import RedirectView

import apps.core.views
from redpot.settings import W2P_REDPOT_URL

urlpatterns = [
    path('login/', apps.core.views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('admin/', admin.site.urls),
    path('amendment/', include('apps.amendment.urls')),
    path('', apps.core.views.index, name='home'),
    path('index/', apps.core.views.index),
    path('enrolment/', include('apps.enrolment.urls')),
    path('fee/', include('apps.fee.urls')),
    path('finance/', include('apps.finance.urls')),
    path('hesa/', include('apps.hesa.urls')),
    path('invoice/', include('apps.invoice.urls')),
    path('programme/', include('apps.programme.urls')),
    path('module/', include('apps.module.urls')),
    path('qa/', include('apps.qualification_aim.urls')),
    path('student/', include('apps.student.urls')),
    path('tutor/', include('apps.tutor.urls')),
    path('tutor-payment/', include('apps.tutor_payment.urls')),
    path('autocomplete/', include('apps.autocomplete.urls')),
    path('user/', include('apps.user.urls')),
    path('staff-list/', include('apps.staff_list.urls')),
    path('staff-forms/', include('apps.staff_forms.urls')),
    path('website-account/', include('apps.website_account.urls')),
    # Example of legacy URLs
    path(
        'student/view/<int:id>',
        RedirectView.as_view(url=f'{W2P_REDPOT_URL}/student/view/%(id)s'),
        name='student-view',
    ),
    path(
        'student/<str:action>/<int:id>',
        RedirectView.as_view(url=f'{W2P_REDPOT_URL}/student/%(action)s/%(id)s'),
        name='student-view',
    ),
    path('unimplemented', page_not_found, {'exception': 'Haven\'t built it yet'}, name='unimplemented'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
