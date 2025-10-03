"""Book display names for different languages."""

from enum import Enum


class BookName(str, Enum):
    GENESIS = "genesis"
    EXODUS = "exodus"
    LEVITICUS = "leviticus"
    NUMBERS = "numbers"
    DEUTERONOMY = "deuteronomy"
    JOSHUA = "joshua"
    JUDGES = "judges"
    RUTH = "ruth"
    SAMUEL_1 = "1samuel"
    SAMUEL_2 = "2samuel"
    KINGS_1 = "1kings"
    KINGS_2 = "2kings"
    CHRONICLES_1 = "1chronicles"
    CHRONICLES_2 = "2chronicles"
    EZRA = "ezra"
    NEHEMIAH = "nehemiah"
    ESTHER = "esther"
    JOB = "job"
    PSALMS = "psalms"
    PROVERBS = "proverbs"
    ECCLESIASTES = "ecclesiastes"
    SONG_OF_SOLOMON = "song-of-solomon"
    ISAIAH = "isaiah"
    JEREMIAH = "jeremiah"
    LAMENTATIONS = "lamentations"
    EZEKIEL = "ezekiel"
    DANIEL = "daniel"
    HOSEA = "hosea"
    JOEL = "joel"
    AMOS = "amos"
    OBADIAH = "obadiah"
    JONAH = "jonah"
    MICAH = "micah"
    NAHUM = "nahum"
    HABAKKUK = "habakkuk"
    ZEPHANIAH = "zephaniah"
    HAGGAI = "haggai"
    ZECHARIAH = "zechariah"
    MALACHI = "malachi"
    MATTHEW = "matthew"
    MARK = "mark"
    LUKE = "luke"
    JOHN = "john"
    ACTS = "acts"
    ROMANS = "romans"
    CORINTHIANS_1 = "1corinthians"
    CORINTHIANS_2 = "2corinthians"
    GALATIANS = "galatians"
    EPHESIANS = "ephesians"
    PHILIPPIANS = "philippians"
    COLOSSIANS = "colossians"
    THESSALONIANS_1 = "1thessalonians"
    THESSALONIANS_2 = "2thessalonians"
    TIMOTHY_1 = "1timothy"
    TIMOTHY_2 = "2timothy"
    TITUS = "titus"
    PHILEMON = "philemon"
    HEBREWS = "hebrews"
    JAMES = "james"
    PETER_1 = "1peter"
    PETER_2 = "2peter"
    JOHN_1 = "1john"
    JOHN_2 = "2john"
    JOHN_3 = "3john"
    JUDE = "jude"
    REVELATION = "revelation"


# Map book names to their canonical Bible order (1-66)
BOOK_ORDER: dict[str, int] = {
    BookName.GENESIS: 1,
    BookName.EXODUS: 2,
    BookName.LEVITICUS: 3,
    BookName.NUMBERS: 4,
    BookName.DEUTERONOMY: 5,
    BookName.JOSHUA: 6,
    BookName.JUDGES: 7,
    BookName.RUTH: 8,
    BookName.SAMUEL_1: 9,
    BookName.SAMUEL_2: 10,
    BookName.KINGS_1: 11,
    BookName.KINGS_2: 12,
    BookName.CHRONICLES_1: 13,
    BookName.CHRONICLES_2: 14,
    BookName.EZRA: 15,
    BookName.NEHEMIAH: 16,
    BookName.ESTHER: 17,
    BookName.JOB: 18,
    BookName.PSALMS: 19,
    BookName.PROVERBS: 20,
    BookName.ECCLESIASTES: 21,
    BookName.SONG_OF_SOLOMON: 22,
    BookName.ISAIAH: 23,
    BookName.JEREMIAH: 24,
    BookName.LAMENTATIONS: 25,
    BookName.EZEKIEL: 26,
    BookName.DANIEL: 27,
    BookName.HOSEA: 28,
    BookName.JOEL: 29,
    BookName.AMOS: 30,
    BookName.OBADIAH: 31,
    BookName.JONAH: 32,
    BookName.MICAH: 33,
    BookName.NAHUM: 34,
    BookName.HABAKKUK: 35,
    BookName.ZEPHANIAH: 36,
    BookName.HAGGAI: 37,
    BookName.ZECHARIAH: 38,
    BookName.MALACHI: 39,
    BookName.MATTHEW: 40,
    BookName.MARK: 41,
    BookName.LUKE: 42,
    BookName.JOHN: 43,
    BookName.ACTS: 44,
    BookName.ROMANS: 45,
    BookName.CORINTHIANS_1: 46,
    BookName.CORINTHIANS_2: 47,
    BookName.GALATIANS: 48,
    BookName.EPHESIANS: 49,
    BookName.PHILIPPIANS: 50,
    BookName.COLOSSIANS: 51,
    BookName.THESSALONIANS_1: 52,
    BookName.THESSALONIANS_2: 53,
    BookName.TIMOTHY_1: 54,
    BookName.TIMOTHY_2: 55,
    BookName.TITUS: 56,
    BookName.PHILEMON: 57,
    BookName.HEBREWS: 58,
    BookName.JAMES: 59,
    BookName.PETER_1: 60,
    BookName.PETER_2: 61,
    BookName.JOHN_1: 62,
    BookName.JOHN_2: 63,
    BookName.JOHN_3: 64,
    BookName.JUDE: 65,
    BookName.REVELATION: 66,
}


def get_book_id(book_name: str) -> int:
    """Get the canonical Bible order ID for a book (1-66)."""
    book_id = BOOK_ORDER.get(book_name)
    if book_id is None:
        raise ValueError(f"Invalid book name: {book_name}")
    return book_id


BOOK_DISPLAY_NAMES: dict[str, dict[str, str]] = {
    "en": {
        BookName.GENESIS: "Genesis",
        BookName.EXODUS: "Exodus",
        BookName.LEVITICUS: "Leviticus",
        BookName.NUMBERS: "Numbers",
        BookName.DEUTERONOMY: "Deuteronomy",
        BookName.JOSHUA: "Joshua",
        BookName.JUDGES: "Judges",
        BookName.RUTH: "Ruth",
        BookName.SAMUEL_1: "1 Samuel",
        BookName.SAMUEL_2: "2 Samuel",
        BookName.KINGS_1: "1 Kings",
        BookName.KINGS_2: "2 Kings",
        BookName.CHRONICLES_1: "1 Chronicles",
        BookName.CHRONICLES_2: "2 Chronicles",
        BookName.EZRA: "Ezra",
        BookName.NEHEMIAH: "Nehemiah",
        BookName.ESTHER: "Esther",
        BookName.JOB: "Job",
        BookName.PSALMS: "Psalms",
        BookName.PROVERBS: "Proverbs",
        BookName.ECCLESIASTES: "Ecclesiastes",
        BookName.SONG_OF_SOLOMON: "Song of Solomon",
        BookName.ISAIAH: "Isaiah",
        BookName.JEREMIAH: "Jeremiah",
        BookName.LAMENTATIONS: "Lamentations",
        BookName.EZEKIEL: "Ezekiel",
        BookName.DANIEL: "Daniel",
        BookName.HOSEA: "Hosea",
        BookName.JOEL: "Joel",
        BookName.AMOS: "Amos",
        BookName.OBADIAH: "Obadiah",
        BookName.JONAH: "Jonah",
        BookName.MICAH: "Micah",
        BookName.NAHUM: "Nahum",
        BookName.HABAKKUK: "Habakkuk",
        BookName.ZEPHANIAH: "Zephaniah",
        BookName.HAGGAI: "Haggai",
        BookName.ZECHARIAH: "Zechariah",
        BookName.MALACHI: "Malachi",
        BookName.MATTHEW: "Matthew",
        BookName.MARK: "Mark",
        BookName.LUKE: "Luke",
        BookName.JOHN: "John",
        BookName.ACTS: "Acts",
        BookName.ROMANS: "Romans",
        BookName.CORINTHIANS_1: "1 Corinthians",
        BookName.CORINTHIANS_2: "2 Corinthians",
        BookName.GALATIANS: "Galatians",
        BookName.EPHESIANS: "Ephesians",
        BookName.PHILIPPIANS: "Philippians",
        BookName.COLOSSIANS: "Colossians",
        BookName.THESSALONIANS_1: "1 Thessalonians",
        BookName.THESSALONIANS_2: "2 Thessalonians",
        BookName.TIMOTHY_1: "1 Timothy",
        BookName.TIMOTHY_2: "2 Timothy",
        BookName.TITUS: "Titus",
        BookName.PHILEMON: "Philemon",
        BookName.HEBREWS: "Hebrews",
        BookName.JAMES: "James",
        BookName.PETER_1: "1 Peter",
        BookName.PETER_2: "2 Peter",
        BookName.JOHN_1: "1 John",
        BookName.JOHN_2: "2 John",
        BookName.JOHN_3: "3 John",
        BookName.JUDE: "Jude",
        BookName.REVELATION: "Revelation",
    },
    "ro": {
        BookName.GENESIS: "Geneza",
        BookName.EXODUS: "Exod",
        BookName.LEVITICUS: "Levitic",
        BookName.NUMBERS: "Numeri",
        BookName.DEUTERONOMY: "Deuteronom",
        BookName.JOSHUA: "Iosua",
        BookName.JUDGES: "Judecători",
        BookName.RUTH: "Rut",
        BookName.SAMUEL_1: "1 Samuel",
        BookName.SAMUEL_2: "2 Samuel",
        BookName.KINGS_1: "1 Regi",
        BookName.KINGS_2: "2 Regi",
        BookName.CHRONICLES_1: "1 Cronici",
        BookName.CHRONICLES_2: "2 Cronici",
        BookName.EZRA: "Ezra",
        BookName.NEHEMIAH: "Neemia",
        BookName.ESTHER: "Estera",
        BookName.JOB: "Iov",
        BookName.PSALMS: "Psalmi",
        BookName.PROVERBS: "Proverbe",
        BookName.ECCLESIASTES: "Eclesiastul",
        BookName.SONG_OF_SOLOMON: "Cântarea Cântărilor",
        BookName.ISAIAH: "Isaia",
        BookName.JEREMIAH: "Ieremia",
        BookName.LAMENTATIONS: "Plângerile lui Ieremia",
        BookName.EZEKIEL: "Ezechiel",
        BookName.DANIEL: "Daniel",
        BookName.HOSEA: "Osea",
        BookName.JOEL: "Ioel",
        BookName.AMOS: "Amos",
        BookName.OBADIAH: "Obadia",
        BookName.JONAH: "Iona",
        BookName.MICAH: "Mica",
        BookName.NAHUM: "Naum",
        BookName.HABAKKUK: "Habacuc",
        BookName.ZEPHANIAH: "Țefania",
        BookName.HAGGAI: "Hagai",
        BookName.ZECHARIAH: "Zaharia",
        BookName.MALACHI: "Maleahi",
        BookName.MATTHEW: "Matei",
        BookName.MARK: "Marcu",
        BookName.LUKE: "Luca",
        BookName.JOHN: "Ioan",
        BookName.ACTS: "Faptele Apostolilor",
        BookName.ROMANS: "Romani",
        BookName.CORINTHIANS_1: "1 Corinteni",
        BookName.CORINTHIANS_2: "2 Corinteni",
        BookName.GALATIANS: "Galateni",
        BookName.EPHESIANS: "Efeseni",
        BookName.PHILIPPIANS: "Filipeni",
        BookName.COLOSSIANS: "Coloseni",
        BookName.THESSALONIANS_1: "1 Tesaloniceni",
        BookName.THESSALONIANS_2: "2 Tesaloniceni",
        BookName.TIMOTHY_1: "1 Timotei",
        BookName.TIMOTHY_2: "2 Timotei",
        BookName.TITUS: "Tit",
        BookName.PHILEMON: "Filimon",
        BookName.HEBREWS: "Evrei",
        BookName.JAMES: "Iacov",
        BookName.PETER_1: "1 Petru",
        BookName.PETER_2: "2 Petru",
        BookName.JOHN_1: "1 Ioan",
        BookName.JOHN_2: "2 Ioan",
        BookName.JOHN_3: "3 Ioan",
        BookName.JUDE: "Iuda",
        BookName.REVELATION: "Apocalipsa",
    },
}


def get_book_display_name(book_key: str, language: str) -> str:
    """Get book display name for a language.

    Args:
        book_key: English book key (e.g., "genesis", "1samuel")
        language: Language code ("en", "ro")

    Returns:
        Display name in the specified language, or the book_key if not found.
    """
    return BOOK_DISPLAY_NAMES.get(language, {}).get(book_key, book_key)


def is_valid_book_name(book_name: str) -> bool:
    """Check if a book name is a valid BookName value."""
    return book_name in BookName._value2member_map_
