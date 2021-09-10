import unicodedata


def normalize(text: str) -> str:
    """Converts or strips out characters invalid in filenames"""

    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
