import unicodedata

from django.utils.functional import lazy
from django.utils.safestring import mark_safe

# Utility for lazily rendering reversed urls in html (e.g. in form help_text)
mark_safe_lazy = lazy(mark_safe, str)


def normalize(text: str) -> str:
    """Converts or strips out characters invalid in filenames

    E.g. 'Éżraç愛' -> 'Ezrac'
    """

    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')


def normalize_to_latin1(text: str) -> str:
    """Converts or strips out characters outside the latin-1 unicode set (HESA spec.)

    E.g. 'Éżraç愛' -> 'Ézraç'
    """

    def convert_char(char: str) -> str:
        try:
            char.encode('latin-1')
        except UnicodeEncodeError:
            char = unicodedata.normalize('NFKD', char).encode('latin-1', 'ignore').decode('latin-1')
        return char

    return ''.join(convert_char(char) for char in text)
