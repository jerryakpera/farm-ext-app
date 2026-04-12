"""
Enums for the `verses` app.
"""

# django_packages
from django.db import models


class BibleVersionChoices(models.TextChoices):
    """
    Choice lists for the version field.
    """

    WEB = "ENGWEBP", "World English Bible"
    KJV = "eng_kjv", "King James Version"


class BibleBookChoices(models.TextChoices):
    """
    Choice list for Bible books using API book IDs.
    """

    @classmethod
    def from_id(cls, book_id: str):
        """
        Return the book enum from the book_id.

        Parameters
        ----------
        book_id : str
            The API book identifier, e.g. "GEN", "EXO".

        Returns
        -------
        BibleBookChoices
            The matching enum member for the given book ID.
        """

        try:
            return cls(book_id)
        except ValueError:
            raise ValueError(f"Invalid Bible book id: {book_id}")

    GEN = "GEN", "Genesis"
    EXO = "EXO", "Exodus"
    LEV = "LEV", "Leviticus"
    NUM = "NUM", "Numbers"
    DEU = "DEU", "Deuteronomy"
    JOS = "JOS", "Joshua"
    JDG = "JDG", "Judges"
    RUT = "RUT", "Ruth"
    SA1 = "1SA", "1 Samuel"
    SA2 = "2SA", "2 Samuel"
    KI1 = "1KI", "1 Kings"
    KI2 = "2KI", "2 Kings"
    CH1 = "1CH", "1 Chronicles"
    CH2 = "2CH", "2 Chronicles"
    EZR = "EZR", "Ezra"
    NEH = "NEH", "Nehemiah"
    EST = "EST", "Esther"
    JOB = "JOB", "Job"
    PSA = "PSA", "Psalms"
    PRO = "PRO", "Proverbs"
    ECC = "ECC", "Ecclesiastes"
    SNG = "SNG", "Song of Solomon"
    ISA = "ISA", "Isaiah"
    JER = "JER", "Jeremiah"
    LAM = "LAM", "Lamentations"
    EZK = "EZK", "Ezekiel"
    DAN = "DAN", "Daniel"
    HOS = "HOS", "Hosea"
    JOL = "JOL", "Joel"
    AMO = "AMO", "Amos"
    OBA = "OBA", "Obadiah"
    JON = "JON", "Jonah"
    MIC = "MIC", "Micah"
    NAM = "NAM", "Nahum"
    HAB = "HAB", "Habakkuk"
    ZEP = "ZEP", "Zephaniah"
    HAG = "HAG", "Haggai"
    ZEC = "ZEC", "Zechariah"
    MAL = "MAL", "Malachi"
    MAT = "MAT", "Matthew"
    MRK = "MRK", "Mark"
    LUK = "LUK", "Luke"
    JHN = "JHN", "John"
    ACT = "ACT", "Acts"
    ROM = "ROM", "Romans"
    CO1 = "1CO", "1 Corinthians"
    CO2 = "2CO", "2 Corinthians"
    GAL = "GAL", "Galatians"
    EPH = "EPH", "Ephesians"
    PHP = "PHP", "Philippians"
    COL = "COL", "Colossians"
    TH1 = "1TH", "1 Thessalonians"
    TH2 = "2TH", "2 Thessalonians"
    TI1 = "1TI", "1 Timothy"
    TI2 = "2TI", "2 Timothy"
    TIT = "TIT", "Titus"
    PHM = "PHM", "Philemon"
    HEB = "HEB", "Hebrews"
    JAS = "JAS", "James"
    PE1 = "1PE", "1 Peter"
    PE2 = "2PE", "2 Peter"
    JN1 = "1JN", "1 John"
    JN2 = "2JN", "2 John"
    JN3 = "3JN", "3 John"
    JUD = "JUD", "Jude"
    REV = "REV", "Revelation"
