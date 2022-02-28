from django import http
from django.conf import settings


def template_settings(request: http.HttpRequest) -> dict:
    """Return a series of settings that used globally for template rendering"""
    return {
        'WARNING_BANNER': settings.WARNING_BANNER,
        'CANONICAL_URL': settings.CANONICAL_URL,  # todo: this setting needs a better name
    }
