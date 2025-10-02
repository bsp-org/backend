import re
import unicodedata


def remove_diacritics(text: str) -> str:
    """Remove diacritics from text for search."""
    nfd = unicodedata.normalize("NFD", text)
    return "".join(char for char in nfd if unicodedata.category(char) != "Mn")


# Map precomposed cedilla -> modern comma-below
_CEDILLA_TO_COMMA = str.maketrans(
    {
        "\u015f": "\u0219",  # ş -> ș
        "\u015e": "\u0218",  # Ş -> Ș
        "\u0163": "\u021b",  # ţ -> ț
        "\u0162": "\u021a",  # Ţ -> Ț
    }
)


def normalize_ro(text: str) -> str:
    """
    Normalize Romanian diacritics to modern comma-below forms (ș, ț)
    and canonical NFC. Also converts combining forms (s/t + U+0326/U+0327).
    """

    # 1) Decompose so combining marks become visible
    t = unicodedata.normalize("NFD", text)

    # 2) s/S or t/T followed by combining comma-below (0326) or cedilla (0327)
    def _repl_s(m):
        return "\u0219" if m.group(1).islower() else "\u0218"  # ș / Ș

    def _repl_t(m):
        return "\u021b" if m.group(1).islower() else "\u021a"  # ț / Ț

    t = re.sub(r"([sS])[\u0326\u0327]", _repl_s, t)
    t = re.sub(r"([tT])[\u0326\u0327]", _repl_t, t)

    # 3) Recompose
    t = unicodedata.normalize("NFC", t)

    # 4) Precomposed cedilla leftovers -> comma-below
    t = t.translate(_CEDILLA_TO_COMMA)

    # 5) Final NFC for good measure
    return unicodedata.normalize("NFC", t)


NORMALIZATION_FUNCTIONS = {"ro": normalize_ro}


def normalize(text: str, language_code: str) -> str:
    return NORMALIZATION_FUNCTIONS[language_code](text)
