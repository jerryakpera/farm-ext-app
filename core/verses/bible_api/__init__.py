"""
``core.verse.bible_api`` — external Bible API integration.

Public surface
--------------
- ``fetch_verse_text`` — retrieve and return scripture text for a reference
- ``BibleApiError`` and its subclasses — for structured error handling
"""

# app_packages
from .client import fetch_verse_text
from .exceptions import (
    BibleApiError,
    BibleApiUnavailableError,
    BibleApiUnexpectedResponseError,
    BibleApiVerseNotFoundError,
)


__all__ = [
    "fetch_verse_text",
    "BibleApiError",
    "BibleApiUnavailableError",
    "BibleApiUnexpectedResponseError",
    "BibleApiVerseNotFoundError",
]
