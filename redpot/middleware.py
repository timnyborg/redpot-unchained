from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin


class IEDetectionMiddleware(MiddlewareMixin):
    """Raise a 403 if Internet Explorer is detected.

    This is used instead instead of DISALLOWED_USER_AGENTS because it can
    be run later than CommonMiddleware (after AuthenticationMiddleware)
    so request.user will exist and the menu can run
    """

    def process_request(self, request):
        user_agent: str = request.META.get('HTTP_USER_AGENT', '').lower()
        if 'trident' in user_agent or 'msie' in user_agent:
            # Todo: consider a stand-alone view or template
            raise PermissionDenied('Redpot cannot be accessed using Internet Explorer')
        return None
