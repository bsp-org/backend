import unicodedata


def normalize_text(text: str) -> str:
    """Remove diacritics from text for search."""
    nfd = unicodedata.normalize("NFD", text)
    return "".join(char for char in nfd if unicodedata.category(char) != "Mn")
