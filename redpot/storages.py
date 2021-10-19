from django.conf import settings
from django.core.files.storage import FileSystemStorage


class WebsiteStorage(FileSystemStorage):
    """Separate storage class for managing website media via mounted folder (e.g. module & tutor images)"""

    def __init__(self):
        super().__init__(location=settings.WEBSITE_MEDIA_ROOT, base_url=settings.WEBSITE_MEDIA_URL)


website_storage = WebsiteStorage()
