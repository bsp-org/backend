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


def _normalize_ro(text: str) -> str:
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


NORMALIZATION_FUNCTIONS = {"ro": _normalize_ro}


def normalize(text: str, language_code: str) -> str:
    return NORMALIZATION_FUNCTIONS[language_code](text)


def _find_match_positions(text: str, query_no_diacritics: str) -> list[tuple[int, int]]:
    """
    Find match positions in text by comparing diacritic-free versions.
    
    This function finds matches in the diacritic-free text, then maps
    those positions back to the original text for highlighting.
    
    Returns list of (start, end) positions in the original text.
    """
    if not query_no_diacritics:
        return []
    
    # Remove diacritics from text for matching
    text_no_diacritics = remove_diacritics(text)
    query_lower = query_no_diacritics.lower()
    text_lower = text_no_diacritics.lower()
    
    positions = []
    start = 0
    
    while True:
        # Find match in diacritic-free text
        pos = text_lower.find(query_lower, start)
        if pos == -1:
            break
        
        # Map positions from diacritic-free text back to original text
        # We need to find which characters in original text correspond to
        # characters at pos and pos+len in the diacritic-free text
        orig_start = _map_diacritic_free_pos_to_original(text, text_no_diacritics, pos)
        orig_end = _map_diacritic_free_pos_to_original(text, text_no_diacritics, pos + len(query_no_diacritics))
        
        positions.append((orig_start, orig_end))
        start = pos + 1
    
    return positions


def _map_diacritic_free_pos_to_original(original: str, diacritic_free: str, pos: int) -> int:
    """
    Map a position in diacritic-free text back to the original text.
    
    Since removing diacritics can only reduce or keep the same length,
    we find the corresponding position by counting characters.
    """
    if pos <= 0:
        return 0
    if pos >= len(diacritic_free):
        return len(original)
    
    # Count how many characters in original correspond to pos characters in diacritic-free
    orig_idx = 0
    diac_free_idx = 0
    
    while diac_free_idx < pos and orig_idx < len(original):
        char = original[orig_idx]
        char_no_diac = remove_diacritics(char)
        if char_no_diac:
            # This character contributes to diacritic-free text
            diac_free_idx += len(char_no_diac)
        orig_idx += 1
    
    return orig_idx


def highlight_matches(text: str, query: str, exact: bool = False, language_code: str | None = None) -> str:
    """
    Highlight matching text with bold HTML tags.

    Args:
        text: The text to search in (should be normalized Romanian text)
        query: The search query
        exact: If True, use exact matching; otherwise use word-based matching
        language_code: Language code for normalization (required for exact matching)

    Returns:
        Text with matches wrapped in <b></b> tags
    """
    if not query:
        return text

    if exact:
        # For exact matching, we need to handle diacritics properly
        # Normalize query and remove diacritics for pattern matching
        if language_code:
            normalized_query = normalize(text=query, language_code=language_code)
        else:
            normalized_query = query
        
        query_no_diacritics = remove_diacritics(normalized_query)
        
        # Find all match positions using diacritic-insensitive pattern
        positions = _find_match_positions(text, query_no_diacritics)
        
        # Build result with highlights, working backwards to preserve positions
        if not positions:
            return text
        
        result = []
        last_end = 0
        for start, end in positions:
            # Add text before match
            if start > last_end:
                result.append(text[last_end:start])
            # Add highlighted match
            result.append(f"<b>{text[start:end]}</b>")
            last_end = end
        
        # Add remaining text
        if last_end < len(text):
            result.append(text[last_end:])
        
        return "".join(result)
    else:
        # Word-based matching - highlight each word independently
        # Remove diacritics for matching but highlight original text
        words = [w.strip() for w in query.split() if w.strip()]
        if not words:
            return text
        
        # For each word, find matches accounting for diacritics
        highlighted_ranges = set()
        
        for word in words:
            word_no_diacritics = remove_diacritics(word)
            positions = _find_match_positions(text, word_no_diacritics)
            for start, end in positions:
                highlighted_ranges.add((start, end))
        
        # Build result with all highlights
        if not highlighted_ranges:
            return text
        
        # Sort ranges by start position
        sorted_ranges = sorted(highlighted_ranges)
        
        # Merge overlapping ranges
        merged = []
        for start, end in sorted_ranges:
            if merged and start <= merged[-1][1]:
                # Merge with previous range
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))
        
        # Build result
        result_parts = []
        last_end = 0
        for start, end in merged:
            if start > last_end:
                result_parts.append(text[last_end:start])
            result_parts.append(f"<b>{text[start:end]}</b>")
            last_end = end
        
        if last_end < len(text):
            result_parts.append(text[last_end:])
        
        return "".join(result_parts)


def normalize_to_slug(text: str) -> str:
    """Normalize a string into slug-friendly form."""
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")
