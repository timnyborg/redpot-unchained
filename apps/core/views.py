import multiprocessing
import os
import platform
import shutil
import time

import django_redis

import django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.views import generic

from apps.core.forms import CustomAuthForm, ImpersonateForm
from apps.core.utils.views import PageTitleMixin


class Index(generic.TemplateView):
    template_name = 'core/index.html'


class CustomLoginView(LoginView):
    authentication_form = CustomAuthForm


class SystemInfo(PermissionRequiredMixin, generic.TemplateView):
    permission_required = 'user.dev'
    template_name = 'core/system_info.html'

    def get_context_data(self, **kwargs):
        disk_usage = shutil.disk_usage("/")
        max_memory = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
        available_memory = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_AVPHYS_PAGES')
        redis_conn = django_redis.get_redis_connection()
        redis_info = redis_conn.info('memory')
        return {
            'cpu_count': multiprocessing.cpu_count(),
            'max_memory': max_memory,
            'used_memory': max_memory - available_memory,
            'uptime': int(time.clock_gettime(time.CLOCK_BOOTTIME)),
            'disk': {
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
            },
            'redis': {
                'total': redis_info['maxmemory'],
                'used': redis_info['used_memory'],
            },
            'library_versions': {
                'python': platform.python_version(),
                'django': django.get_version(),
            },
        }


class Impersonate(PermissionRequiredMixin, PageTitleMixin, generic.FormView):
    """A screen for quick user impersonation, requiring a superuser"""

    template_name = 'core/impersonate.html'
    form_class = ImpersonateForm
    title = 'User'
    subtitle = 'Impersonate'

    def has_permission(self) -> bool:
        return self.request.user.is_superuser
