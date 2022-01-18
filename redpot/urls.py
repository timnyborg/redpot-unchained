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

import apps.core.views as core_views

urlpatterns = [
    path('login/', core_views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('admin/', admin.site.urls),
    path('amendment/', include('apps.amendment.urls')),
    path('application/', include('apps.application.urls')),
    path('', core_views.Index.as_view(), name='home'),
    path('index/', core_views.Index.as_view()),
    path('system-info/', core_views.SystemInfo.as_view(), name='system-info'),
    path('booking/', include('apps.booking.urls')),
    path('contract/', include('apps.contract.urls')),
    path('discount/', include('apps.discount.urls')),
    path('enrolment/', include('apps.enrolment.urls')),
    path('fee/', include('apps.fee.urls')),
    path('finance/', include('apps.finance.urls')),
    path('hesa/', include('apps.hesa.urls')),
    path('invoice/', include('apps.invoice.urls')),
    path('programme/', include('apps.programme.urls')),
    path('proposal/', include('apps.proposal.urls')),
    path('module/', include('apps.module.urls')),
    path('qa/', include('apps.qualification_aim.urls')),
    path('student/', include('apps.student.urls')),
    path('transcript/', include('apps.transcript.urls')),
    path('tutor/', include('apps.tutor.urls')),
    path('tutor-payment/', include('apps.tutor_payment.urls')),
    path('autocomplete/', include('apps.autocomplete.urls')),
    path('user/', include('apps.user.urls')),
    path('staff-list/', include('apps.staff_list.urls')),
    path('feedback/', include('apps.feedback.urls')),
    path('staff-forms/', include('apps.staff_forms.urls')),
    path('task/', include('apps.task_progress.urls', namespace='task')),
    path('waitlist/', include('apps.waitlist.urls')),
    path('website-account/', include('apps.website_account.urls')),
    # django-hijack urls for impersonation
    path('impersonate', core_views.Impersonate.as_view(), name='impersonate'),
    path('impersonate-api/', include('hijack.urls')),
    path('unimplemented', page_not_found, {'exception': 'Haven\'t built it yet'}, name='unimplemented'),
    # django-ckeditor urls for uploads
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
