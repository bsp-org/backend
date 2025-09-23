#!/usr/bin/env python3
"""
Cornilescu Bible Data Extractor
"""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import requests

# USFX book code mapping (from the actual XML file)
USFX_BOOK_MAPPING = {
    # Old Testament
    "gen": "genesis",
    "exo": "exodus",
    "lev": "leviticus",
    "num": "numbers",
    "deu": "deuteronomy",
    "jos": "joshua",
    "jdg": "judges",
    "rut": "ruth",
    "1sa": "1samuel",
    "2sa": "2samuel",
    "1ki": "1kings",
    "2ki": "2kings",
    "1ch": "1chronicles",
    "2ch": "2chronicles",
    "ezr": "ezra",
    "neh": "nehemiah",
    "est": "esther",
    "job": "job",
    "psa": "psalms",
    "pro": "proverbs",
    "ecc": "ecclesiastes",
    "sng": "song-of-solomon",
    "isa": "isaiah",
    "jer": "jeremiah",
    "lam": "lamentations",
    "ezk": "ezekiel",
    "dan": "daniel",
    "hos": "hosea",
    "jol": "joel",
    "amo": "amos",
    "oba": "obadiah",
    "jon": "jonah",
    "mic": "micah",
    "nam": "nahum",
    "hab": "habakkuk",
    "zep": "zephaniah",
    "hag": "haggai",
    "zec": "zechariah",
    "mal": "malachi",
    # New Testament
    "mat": "matthew",
    "mrk": "mark",
    "luk": "luke",
    "jhn": "john",
    "act": "acts",
    "rom": "romans",
    "1co": "1corinthians",
    "2co": "2corinthians",
    "gal": "galatians",
    "eph": "ephesians",
    "php": "philippians",
    "col": "colossians",
    "1th": "1thessalonians",
    "2th": "2thessalonians",
    "1ti": "1timothy",
    "2ti": "2timothy",
    "tit": "titus",
    "phm": "philemon",
    "heb": "hebrews",
    "jas": "james",
    "1pe": "1peter",
    "2pe": "2peter",
    "1jn": "1john",
    "2jn": "2john",
    "3jn": "3john",
    "jud": "jude",
    "rev": "revelation",
}

# Romanian book name mapping (for JSON sources)
ROMANIAN_BOOK_MAPPING = {
    "geneza": "genesis",
    "exod": "exodus",
    "levitic": "leviticus",
    "numeri": "numbers",
    "deuteronom": "deuteronomy",
    "iosua": "joshua",
    "judecatori": "judges",
    "rut": "ruth",
    "1samuel": "1samuel",
    "2samuel": "2samuel",
    "1regi": "1kings",
    "2regi": "2kings",
    "1cronici": "1chronicles",
    "2cronici": "2chronicles",
    "ezra": "ezra",
    "neemia": "nehemiah",
    "estera": "esther",
    "iov": "job",
    "psalmi": "psalms",
    "proverbe": "proverbs",
    "eclesiastul": "ecclesiastes",
    "cantarea": "song-of-solomon",
    "isaia": "isaiah",
    "ieremia": "jeremiah",
    "plangerile": "lamentations",
    "ezechiel": "ezekiel",
    "daniel": "daniel",
    "osea": "hosea",
    "ioel": "joel",
    "amos": "amos",
    "obadia": "obadiah",
    "iona": "jonah",
    "mica": "micah",
    "naum": "nahum",
    "habacuc": "habakkuk",
    "tefania": "zephaniah",
    "hagai": "haggai",
    "zaharia": "zechariah",
    "maleahi": "malachi",
    "matei": "matthew",
    "marcu": "mark",
    "luca": "luke",
    "ioan": "john",
    "faptele": "acts",
    "romani": "romans",
    "1corinteni": "1corinthians",
    "2corinteni": "2corinthians",
    "galateni": "galatians",
    "efeseni": "ephesians",
    "filipeni": "philippians",
    "coloseni": "colossians",
    "1tesaloniceni": "1thessalonians",
    "2tesaloniceni": "2thessalonians",
    "1timotei": "1timothy",
    "2timotei": "2timothy",
    "tit": "titus",
    "filimon": "philemon",
    "evrei": "hebrews",
    "iacov": "james",
    "1petru": "1peter",
    "2petru": "2peter",
    "1ioan": "1john",
    "2ioan": "2john",
    "3ioan": "3john",
    "iuda": "jude",
    "apocalipsa": "revelation",
}

USFX_IGNORE_TEXT_TAGS = {"f", "x", "fe", "fd", "rq", "note", "footnote"}


def _strip_tag(tag: str) -> str:
    """Drop any XML namespace from a tag."""
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _clean_whitespace(s: str) -> str:
    s = re.sub(r"\s+", " ", s)
    # Trim spaces before punctuation like „ ” ! ? : ; , .
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)
    return s.strip()


def parse_usfx_xml(xml_content: str) -> list[dict[str, Any]]:
    """
    Parse USFX XML Bible content that uses <c id="…"/> and <v id="…"/> markers.
    Collects verse text from tag tails in document order.
    Returns: list of dicts: {book, book_code, chapter, verse, text}
    """
    verses: list[dict[str, Any]] = []

    try:
        root = ET.fromstring(xml_content)  # noqa: S314
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return verses

    def flush_verse_content(verses_list, book_name, chapter, verse, text_parts):
        """If we have buffered text for a verse, push it to results."""
        if chapter is None or verse is None:
            text_parts.clear()
            return
        text = _clean_whitespace("".join(text_parts))
        if text:
            verses_list.append(
                {
                    "book": book_name,
                    "chapter": int(chapter),
                    "verse": int(verse),
                    "text": text,
                }
            )
        text_parts.clear()

    # Iterate books
    for book in root.iter():
        if _strip_tag(book.tag) != "book":
            continue

        book_code_src = (book.get("id") or "").lower()
        book_code = book_code_src or ""
        book_english = USFX_BOOK_MAPPING.get(book_code, book_code or "unknown")

        current_chapter: int | None = None
        current_verse: int | None = None
        buf_parts: list[str] = []

        # Walk descendants in document order
        for node in book.iter():
            if node is book:
                # Ignore book.text; verses start at <c>/<v>
                continue

            tag = _strip_tag(node.tag)

            if tag == "book":
                # Safety: don't descend into nested books
                continue

            if tag == "c":
                # New chapter: close any open verse, set chapter
                flush_verse_content(verses, book_english, current_chapter, current_verse, buf_parts)
                cid = node.get("id") or node.get("c") or node.get("number")
                try:
                    current_chapter = int(re.sub(r"\D+", "", cid)) if cid else None
                except ValueError:
                    current_chapter = None
                current_verse = None  # we'll wait for first <v>
                # we don't collect chapter node text; only verse tails
                continue

            if tag == "v":
                # New verse: close previous, set verse, start buffering its tails
                flush_verse_content(verses, book_english, current_chapter, current_verse, buf_parts)
                vid = node.get("id") or node.get("v") or node.get("number")
                try:
                    current_verse = int(re.sub(r"\D+", "", vid)) if vid else None
                except ValueError:
                    current_verse = None

                # <v> is usually empty; verse text is in node.tail
                if current_verse is not None:
                    if node.text:
                        buf_parts.append(node.text)
                    if node.tail:
                        buf_parts.append(node.tail)
                continue

            # Any other node encountered while inside a verse:
            if current_verse is not None:
                # Optionally ignore footnotes/cross-refs content
                if _strip_tag(node.tag) in USFX_IGNORE_TEXT_TAGS:
                    if node.tail:
                        buf_parts.append(node.tail)  # but keep following plain text
                    continue

                if node.text:
                    buf_parts.append(node.text)
                if node.tail:
                    buf_parts.append(node.tail)

        # End of book: flush last verse if any
        flush_verse_content(verses, book_english, current_chapter, current_verse, buf_parts)

    print(f"✓ Parsed {len(verses)} verses from USFX XML")
    return verses


def parse_json_bible(data: list[dict]) -> list[dict[str, Any]]:
    """Parse JSON formatted Bible data."""
    verses = []

    try:
        for book in data:
            if isinstance(book, dict):
                book_name = book.get("book", book.get("name", "")).lower()
                chapters = book.get("chapters", [])

                # Map Romanian book name to English for consistency
                book_english = ROMANIAN_BOOK_MAPPING.get(book_name, book_name)

                for chapter_idx, chapter_verses in enumerate(chapters, 1):
                    for verse_idx, verse_text in enumerate(chapter_verses, 1):
                        if verse_text and verse_text.strip():
                            verses.append(
                                {
                                    "book": book_english,
                                    "chapter": chapter_idx,
                                    "verse": verse_idx,
                                    "text": verse_text.strip(),
                                }
                            )

    except Exception as e:
        print(f"Error parsing JSON: {e}")

    return verses


def extract_vdcc() -> dict[str, Any]:
    """Extract Romanian Corrected Cornilescu Version (VDCC) from USFX XML."""
    url = "https://raw.githubusercontent.com/seven1m/open-bibles/master/ron-rccv.usfx.xml"

    try:
        print("Downloading Romanian Corrected Cornilescu (VDCC) from USFX XML...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        verses = parse_usfx_xml(response.text)

        result = {
            "translation": "VDCC",
            "full_name": "Versiunea Dumitru Cornilescu Corectată",
            "language": "Romanian",
            "format": "USFX XML",
            "source_url": url,
            "verse_count": len(verses),
            "verses": verses,
        }

        print(f"✓ Successfully extracted {len(verses)} verses from VDCC XML")
        return result

    except Exception as e:
        print(f"Error extracting VDCC XML: {e}")
        return {}


def extract_vdc() -> dict[str, Any]:
    """Extract Cornilescu JSON version."""
    url = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/ro_cornilescu.json"

    try:
        print("Downloading Romanian Cornilescu...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Handle BOM by decoding with utf-8-sig
        content = response.content.decode("utf-8-sig")
        data = json.loads(content)
        verses = parse_json_bible(data)

        result = {
            "translation": "VDC",
            "full_name": "Versiunea Dumitru Cornilescu",
            "language": "Romanian",
            "source_url": url,
            "verse_count": len(verses),
            "verses": verses,
        }

        print(f"✓ Successfully extracted {len(verses)} verses from VDC JSON")
        return result

    except Exception as e:
        print(f"Error extracting VDC JSON: {e}")
        return {}


def save_to_json(data: dict[str, Any], filename: str, output_dir: str = "data") -> Path:
    """Save extracted data to JSON file."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    filepath = output_path / filename

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ Saved data to: {filepath}")
        return filepath

    except Exception as e:
        print(f"Error saving to {filepath}: {e}")
        raise


def main():
    """Run the Cornilescu extraction."""
    print("=" * 60)
    print("CORNILESCU BIBLE DATA EXTRACTOR")
    print("=" * 60)
    print("Extracting Romanian Bible translations...")
    print()

    # Extract VDCC (Public Domain USFX XML)
    vdcc_data = extract_vdcc()
    if vdcc_data:
        save_to_json(vdcc_data, "cornilescu_vdcc.json")
        print(f"  → {vdcc_data['verse_count']} verses saved")

    vdc_data = extract_vdc()
    if vdc_data:
        save_to_json(vdc_data, "cornilescu_vdc.json")
        print(f"  → {vdc_data['verse_count']} verses saved")

    print()
    print("=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
