"""
Validate functions for the `verses` app.
"""

# other_apps_packages
from core.verses.bible_structure import BIBLE_VERSE_MAP
from core.verses.choices import BibleBookChoices, BibleVersionChoices
from core.verses.constants import MEMORY_VERSE_MAX_LENGTH
from core.verses.exceptions import VerseValidationError


def validate_bible_version(version):
    """
    Validate that a Bible translation version is supported.

    Parameters
    ----------
    version : str
        Bible translation key (e.g. "eng_kjv", "ENGWEBP").

    Returns
    -------
    None
        Raises VerseValidationError if the version is not supported.
    """

    valid_versions = BibleVersionChoices.values

    if version not in valid_versions:
        raise VerseValidationError(
            f"'{version}' is not a supported Bible version. "
            f"Supported versions are: {', '.join(valid_versions)}."
        )


def validate_bible_book(book):
    """
    Validate that a Bible book identifier is recognised.

    Parameters
    ----------
    book : str
        Bible book identifier (e.g. "GEN", "EXO").

    Returns
    -------
    None
        Raises VerseValidationError if the book is not recognised.
    """

    valid_books = BibleBookChoices.values

    if book not in valid_books:
        raise VerseValidationError(f"'{book}' is not a recognised book.")


def validate_chapter_verse(
    book,
    chapter,
    verse_start,
    verse_end,
):
    """
    Validate that a chapter and verse range exists within a Bible book.

    Parameters
    ----------
    book : str
        Bible book identifier (e.g. "GEN", "EXO").
    chapter : int
        Chapter number within the book.
    verse_start : int
        Starting verse number.
    verse_end : int | None
        Ending verse number, or None if only a single verse is selected.

    Returns
    -------
    None
        Raises VerseValidationError if any part of the reference is invalid.
    """

    book_chapters = BIBLE_VERSE_MAP[book]

    # chapter must exist in the book
    if chapter not in book_chapters:
        raise VerseValidationError(f"{book} does not have a chapter {chapter}.")

    chapter_verse_count = book_chapters[chapter]

    # verse_start must be within the chapter
    if not (1 <= verse_start <= chapter_verse_count):
        raise VerseValidationError(
            f"Verse {verse_start} does not exist in {book} {chapter}. "
            f"Valid verses are 1–{chapter_verse_count}."
        )

    if verse_end is not None:
        # verse_end must be strictly greater than verse_start
        if verse_end <= verse_start:
            raise VerseValidationError(
                f"verse_end ({verse_end}) must be greater than "
                f"verse_start ({verse_start})."
            )

        # span must not exceed 3 consecutive verses
        if verse_end - verse_start > {MEMORY_VERSE_MAX_LENGTH - 1}:
            raise VerseValidationError(
                f"A memory verse may span at most {MEMORY_VERSE_MAX_LENGTH} consecutive verses. "
                f"The requested range ({verse_start}–{verse_end}) spans "
                f"{verse_end - verse_start + 1} verses."
            )

        # verse_end must be within the chapter
        if verse_end > chapter_verse_count:
            raise VerseValidationError(
                f"Verse {verse_end} does not exist in {book} {chapter}. "
                f"Valid verses are 1–{chapter_verse_count}."
            )
