from typing import Optional

from django.http import HttpRequest
from django.utils import encoding, http


def next_url_if_safe(request: HttpRequest) -> Optional[str]:
    """Returns the supplied url if it is safe from open redirects, and otherwise false
    Allows for concisely redirecting to a 'next' url param, falling back to a default if invalid or None:

    def get_success_url(self):
        return next_url_if_safe(request) or self.object.get_absolute_url()
    """
    url = request.GET.get('next')
    if http.url_has_allowed_host_and_scheme(url, allowed_hosts=None):
        return encoding.iri_to_uri(url)
    return None
