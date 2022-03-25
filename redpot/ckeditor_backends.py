from io import BytesIO

from ckeditor_uploader.backends import PillowBackend
from PIL import Image

from django.conf import settings

MAX_WIDTH, MAX_HEIGHT = getattr(settings, "MAX_IMAGE_DIMENSIONS", (1600, 1600))


class ResizingPillowBackend(PillowBackend):
    """Modifies django-ckeditor's built-in image-saving backend to enforce maximum dimensions (MAX_IMAGE_DIMENSIONS)"""

    def _compress_image(self, image) -> BytesIO:
        quality = getattr(settings, "CKEDITOR_IMAGE_QUALITY", 75)
        image = image.resize(image.size, Image.ANTIALIAS).convert("RGB")
        if image.width > MAX_WIDTH or image.height > MAX_HEIGHT:
            image.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.ANTIALIAS)
        image_tmp = BytesIO()
        image.save(image_tmp, format="JPEG", quality=quality, optimize=True)
        return image_tmp
