"""
Service layer for the ``core.verse`` app.
"""

# python_packages
import logging

# other_apps_packages
from core.verses import validations

# local
from core.verses.bible_api.client import fetch_verse_text
from core.verses.bible_api.exceptions import BibleApiError
from core.verses.bible_structure import BIBLE_VERSE_MAP
from core.verses.choices import BibleVersionChoices
from core.verses.exceptions import VerseValidationError
from core.verses.models import MemoryVerse, SingleVerse


logger = logging.getLogger(__name__)


# ── Public entry point ────────────────────────────────────────────────────────


def get_or_create_memory_verse(
    *,
    book: str,
    chapter: int,
    verse_start: int,
    verse_end: int | None = None,
    version: str,
    created_by,
) -> tuple[MemoryVerse, bool]:
    """
    Return a ``(MemoryVerse, created)`` tuple for the given reference.

    Parameters
    ----------
    book : str
        Bible book ID matching ``BibleBookChoices``, e.g. ``"1JN"``.
    chapter : int
        Chapter number.
    verse_start : int
        First (or only) verse number.
    verse_end : int | None
        Last verse number for a range. ``None`` for a single verse.
    version : str
        Bible translation key matching ``BibleVersionChoices``,
        e.g. ``"ENGWEBP"``.
    created_by : User
        The user initiating the request. Stored on the ``MemoryVerse``
        record only when it is first created.

    Returns
    -------
    tuple[MemoryVerse, bool]
        ``(instance, created)`` — ``created`` is ``True`` only when a new
        ``MemoryVerse`` row was inserted.
    """

    # Validate all memory verses
    validations.validate_memory_verse(
        book=book,
        chapter=chapter,
        verse_start=verse_start,
        verse_end=verse_end,
        version=version,
    )

    # Step 2 — short-circuit if the MemoryVerse already exists
    existing = validations.find_existing_memory_verse(
        book=book,
        chapter=chapter,
        verse_start=verse_start,
        verse_end=verse_end,
        version=version,
    )

    if existing is not None:
        logger.debug(
            "MemoryVerse already exists | book=%s chapter=%s verses=%s-%s version=%s",
            book,
            chapter,
            verse_start,
            verse_end,
            version,
        )
        return existing, False

    verse_numbers = _verse_range(verse_start, verse_end)
    texts = _fetch_individual_verse_texts(
        book=book,
        chapter=chapter,
        verse_numbers=verse_numbers,
        version=version,
    )

    single_verses = _upsert_single_verses(
        book=book,
        chapter=chapter,
        version=version,
        verse_texts=texts,
    )

    sv_start = single_verses[verse_start]
    sv_end = single_verses[verse_end] if verse_end is not None else None

    memory_verse, created = MemoryVerse.objects.get_or_create(
        verse_start=sv_start,
        verse_end=sv_end,
        defaults={"created_by": created_by},
    )

    logger.info(
        "MemoryVerse %s | id=%s book=%s chapter=%s verses=%s-%s version=%s",
        "created" if created else "resolved",
        memory_verse.pk,
        book,
        chapter,
        verse_start,
        verse_end,
        version,
    )

    return memory_verse, created


def _verse_range(verse_start: int, verse_end: int | None) -> list[int]:
    """
    Return the ordered list of verse numbers for this selection.

    Parameters
    ----------
    verse_start : int
        The starting verse number.
    verse_end : int | None
        The ending verse number, if provided.

    Returns
    -------
    list[int]
        A list of verse numbers in ascending order.
    """

    end = verse_end if verse_end is not None else verse_start

    return list(range(verse_start, end + 1))


def _fetch_individual_verse_texts(
    *,
    book: str,
    chapter: int,
    verse_numbers: list[int],
    version: str,
) -> dict[int, str]:
    """
    Fetch the chapter once from the external API and extract each
    individual verse text.

    Parameters
    ----------
    book : str
        Bible book identifier (e.g. "GEN").
    chapter : int
        Chapter number within the book.
    verse_numbers : list[int]
        List of verse numbers to fetch.
    version : str
        Bible translation key (e.g. "eng_kjv").

    Returns
    -------
    dict[int, str]
        Mapping of verse number to verse text.
    """

    texts: dict[int, str] = {}

    for verse_number in verse_numbers:
        text = fetch_verse_text(
            translation=version,
            book=book,
            chapter=chapter,
            verse_start=verse_number,
            verse_end=verse_number,
        )
        texts[verse_number] = text

    return texts


def _upsert_single_verses(
    *,
    book: str,
    chapter: int,
    version: str,
    verse_texts: dict[int, str],
) -> dict[int, SingleVerse]:
    """
    Get-or-create a ``SingleVerse`` row for each verse number in
    ``verse_texts``.

    Parameters
    ----------
    book : str
        Bible book identifier (e.g. "GEN").
    chapter : int
        Chapter number within the book.
    version : str
        Bible translation key (e.g. "eng_kjv").
    verse_texts : dict[int, str]
        Mapping of verse numbers to verse text content.

    Returns
    -------
    dict[int, SingleVerse]
        Mapping of verse number to ``SingleVerse`` model instances.
    """

    result: dict[int, SingleVerse] = {}

    for verse_number, text in verse_texts.items():
        sv, _ = SingleVerse.objects.get_or_create(
            book=book,
            chapter=chapter,
            verse=verse_number,
            version=version,
            defaults={"text": text},
        )
        result[verse_number] = sv

    return result
