"""
Validate unique memory verse.
"""

# other_apps_packages
from core.verses.models import MemoryVerse


def find_existing_memory_verse(
    *,
    book: str,
    chapter: int,
    verse_start: int,
    verse_end: int | None,
    version: str,
) -> MemoryVerse | None:
    """
    Return an existing ``MemoryVerse`` for this reference if one exists,
    otherwise return ``None``.

    Parameters
    ----------
    book : str
        Bible book identifier (e.g. "GEN", "EXO").
    chapter : int
        Chapter number within the book.
    verse_start : int
        Starting verse number.
    verse_end : int | None
        Ending verse number, or None if the reference is a single verse.
    version : str
        Bible translation key (e.g. "eng_kjv", "ENGWEBP").

    Returns
    -------
    MemoryVerse | None
        The matching MemoryVerse instance if found, otherwise None.
    """

    qs = MemoryVerse.objects.filter(
        verse_start__book=book,
        verse_start__chapter=chapter,
        verse_start__verse=verse_start,
        verse_start__version=version,
    ).select_related("verse_start", "verse_end", "created_by")

    if verse_end is None:
        qs = qs.filter(verse_end__isnull=True)
    else:
        qs = qs.filter(
            verse_end__verse=verse_end,
            verse_end__isnull=False,
        )

    return qs.first()
