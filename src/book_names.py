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


BOOK_DISPLAY_NAMES: dict[str, dict[str, str]] = {
    "en": {
        "genesis": "Genesis",
        "exodus": "Exodus",
        "leviticus": "Leviticus",
        "numbers": "Numbers",
        "deuteronomy": "Deuteronomy",
        "joshua": "Joshua",
        "judges": "Judges",
        "ruth": "Ruth",
        "1samuel": "1 Samuel",
        "2samuel": "2 Samuel",
        "1kings": "1 Kings",
        "2kings": "2 Kings",
        "1chronicles": "1 Chronicles",
        "2chronicles": "2 Chronicles",
        "ezra": "Ezra",
        "nehemiah": "Nehemiah",
        "esther": "Esther",
        "job": "Job",
        "psalms": "Psalms",
        "proverbs": "Proverbs",
        "ecclesiastes": "Ecclesiastes",
        "song-of-solomon": "Song of Solomon",
        "isaiah": "Isaiah",
        "jeremiah": "Jeremiah",
        "lamentations": "Lamentations",
        "ezekiel": "Ezekiel",
        "daniel": "Daniel",
        "hosea": "Hosea",
        "joel": "Joel",
        "amos": "Amos",
        "obadiah": "Obadiah",
        "jonah": "Jonah",
        "micah": "Micah",
        "nahum": "Nahum",
        "habakkuk": "Habakkuk",
        "zephaniah": "Zephaniah",
        "haggai": "Haggai",
        "zechariah": "Zechariah",
        "malachi": "Malachi",
        "matthew": "Matthew",
        "mark": "Mark",
        "luke": "Luke",
        "john": "John",
        "acts": "Acts",
        "romans": "Romans",
        "1corinthians": "1 Corinthians",
        "2corinthians": "2 Corinthians",
        "galatians": "Galatians",
        "ephesians": "Ephesians",
        "philippians": "Philippians",
        "colossians": "Colossians",
        "1thessalonians": "1 Thessalonians",
        "2thessalonians": "2 Thessalonians",
        "1timothy": "1 Timothy",
        "2timothy": "2 Timothy",
        "titus": "Titus",
        "philemon": "Philemon",
        "hebrews": "Hebrews",
        "james": "James",
        "1peter": "1 Peter",
        "2peter": "2 Peter",
        "1john": "1 John",
        "2john": "2 John",
        "3john": "3 John",
        "jude": "Jude",
        "revelation": "Revelation",
    },
    "ro": {
        "genesis": "Geneza",
        "exodus": "Exod",
        "leviticus": "Levitic",
        "numbers": "Numeri",
        "deuteronomy": "Deuteronom",
        "joshua": "Iosua",
        "judges": "Judecători",
        "ruth": "Rut",
        "1samuel": "1 Samuel",
        "2samuel": "2 Samuel",
        "1kings": "1 Regi",
        "2kings": "2 Regi",
        "1chronicles": "1 Cronici",
        "2chronicles": "2 Cronici",
        "ezra": "Ezra",
        "nehemiah": "Neemia",
        "esther": "Estera",
        "job": "Iov",
        "psalms": "Psalmi",
        "proverbs": "Proverbe",
        "ecclesiastes": "Eclesiastul",
        "song-of-solomon": "Cântarea Cântărilor",
        "isaiah": "Isaia",
        "jeremiah": "Ieremia",
        "lamentations": "Plângerile lui Ieremia",
        "ezekiel": "Ezechiel",
        "daniel": "Daniel",
        "hosea": "Osea",
        "joel": "Ioel",
        "amos": "Amos",
        "obadiah": "Obadia",
        "jonah": "Iona",
        "micah": "Mica",
        "nahum": "Naum",
        "habakkuk": "Habacuc",
        "zephaniah": " Țefania",
        "haggai": "Hagai",
        "zechariah": "Zaharia",
        "malachi": "Maleahi",
        "matthew": "Matei",
        "mark": "Marcu",
        "luke": "Luca",
        "john": "Ioan",
        "acts": "Faptele Apostolilor",
        "romans": "Romani",
        "1corinthians": "1 Corinteni",
        "2corinthians": "2 Corinteni",
        "galatians": "Galateni",
        "ephesians": "Efeseni",
        "philippians": "Filipeni",
        "colossians": "Coloseni",
        "1thessalonians": "1 Tesaloniceni",
        "2thessalonians": "2 Tesaloniceni",
        "1timothy": "1 Timotei",
        "2timothy": "2 Timotei",
        "titus": "Tit",
        "philemon": "Filimon",
        "hebrews": "Evrei",
        "james": "Iacov",
        "1peter": "1 Petru",
        "2peter": "2 Petru",
        "1john": "1 Ioan",
        "2john": "2 Ioan",
        "3john": "3 Ioan",
        "jude": "Iuda",
        "revelation": "Apocalipsa",
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
