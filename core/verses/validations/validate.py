"""
Validations for the `verses` app.
"""

# app_packages
from . import validate_memory_verse as validations


def validate_memory_verse(
    *,
    book: str,
    chapter: int,
    verse_start: int,
    verse_end: int | None,
    version: str,
) -> None:
    """
    Run all business rule checks defined in core.verses.valiadtions.validate_memory_verse.

    Parameters
    ----------
    book : str
        Bible book identifier (e.g. "GEN", "EXO").
    chapter : int
        Chapter number within the selected book.
    verse_start : int
        Starting verse number.
    verse_end : int | None
        Ending verse number, or None if the reference is a single verse.
    version : str
        Bible translation key (e.g. "eng_kjv", "ENGWEBP").

    Returns
    -------
    None
        This function does not return a value; it raises exceptions if validation fails.
    """

    # version must be a known choice
    validations.validate_bible_version(version)

    # book must exist in the verse map
    validations.validate_bible_book(book)

    validations.validate_chapter_verse(
        book=book,
        chapter=chapter,
        verse_start=verse_start,
        verse_end=verse_end,
    )
