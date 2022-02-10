from storages.backends.sftpstorage import SFTPStorage

from django.conf import settings


class WebsiteStorage(SFTPStorage):
    """Separate storage class for managing website media over SFTP (e.g. module & tutor images)

    If an SFTP target isn't configured via settings, uploads will fail.
    If this is a problem in dev, we may want a setting to choose between SFTPStorage and local filesystem storage
    """

    host = settings.WEBSITE_MEDIA_SFTP_HOST
    params = settings.WEBSITE_MEDIA_SFTP_PARAMS
    root_path = settings.WEBSITE_MEDIA_SFTP_ROOT
    base_url = settings.WEBSITE_MEDIA_URL
