from django import http
from django.conf import settings


def template_settings(request: http.HttpRequest) -> dict:
    """Return a series of settings that are used globally for template rendering"""
    return {
        'WARNING_BANNER': settings.WARNING_BANNER,
        'CANONICAL_URL': settings.CANONICAL_URL,  # todo: this setting needs a better name
        'PUBLIC_WEBSITE_URL': settings.PUBLIC_WEBSITE_URL,
        'PUBLIC_APPS_URL': settings.PUBLIC_APPS_URL,
        'REDPOT_DOCS_URL': settings.REDPOT_DOCS_URL,
        'GOOGLE_TAG_MANAGER_ID': settings.GOOGLE_TAG_MANAGER_ID,
    }
