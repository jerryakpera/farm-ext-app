"""
Responsible for all communication with the external Bible API.
"""

# python_packages
import logging

# third_party_packages
import requests

from decouple import config

# other_apps_packages
# local
from core.verses.bible_api.exceptions import (
    BibleApiUnavailableError,
    BibleApiUnexpectedResponseError,
    BibleApiVerseNotFoundError,
)


logger = logging.getLogger(__name__)

_BASE_URL = config("BIBLE_API_BASE_URL")
_REQUEST_TIMEOUT_SECONDS = 10


def fetch_verse_text(
    *,
    translation: str,
    book: str,
    chapter: int,
    verse_start: int,
    verse_end: int | None = None,
) -> str:
    """
    Return the scripture text for the requested reference.

    Parameters
    ----------
    translation : str
        Bible translation key, e.g. ``"ENGWEBP"`` or ``"eng_kjv"``.
    book : str
        Book name as expected by the API, e.g. ``"1John"`` or ``"Genesis"``.
    chapter : int
        Chapter number.
    verse_start : int
        First (or only) verse number to retrieve.
    verse_end : int | None
        Last verse number when retrieving a range. ``None`` for a single verse.

    Returns
    -------
    str
        The scripture text. Multi-verse references are joined with a single
        space.
    """

    payload = _fetch_chapter(
        translation=translation,
        book=book,
        chapter=chapter,
    )

    verses = _extract_verses(
        payload=payload,
        translation=translation,
        book=book,
        chapter=chapter,
        verse_start=verse_start,
        verse_end=verse_end,
    )

    return _join_verse_texts(verses)


# ── Private helpers ───────────────────────────────────────────────────────────


def _fetch_chapter(*, translation: str, book: str, chapter: int) -> dict:
    """
    Call the external API for one chapter and return the parsed JSON payload.

    Parameters
    ----------
    translation : str
        Bible translation key.
    book : str
        Book name as expected by the API.
    chapter : int
        Chapter number.

    Returns
    -------
    dict
        Parsed JSON response body.
    """

    url = f"{_BASE_URL}/{translation}/{book}/{chapter}.json"

    logger.debug("Fetching Bible chapter | url=%s", url)

    try:
        response = requests.get(url, timeout=_REQUEST_TIMEOUT_SECONDS)
    except requests.exceptions.ConnectionError as exc:
        logger.warning("Bible API connection error | url=%s | error=%s", url, exc)
        raise BibleApiUnavailableError(
            "Could not connect to the Bible API. Please try again later."
        ) from exc
    except requests.exceptions.Timeout as exc:
        logger.warning("Bible API request timed out | url=%s", url)
        raise BibleApiUnavailableError(
            "The Bible API did not respond in time. Please try again later."
        ) from exc
    except requests.exceptions.RequestException as exc:
        logger.warning("Bible API request failed | url=%s | error=%s", url, exc)
        raise BibleApiUnavailableError(
            "An error occurred while contacting the Bible API."
        ) from exc

    if response.status_code == 404:
        logger.info(
            "Bible API returned 404 | translation=%s book=%s chapter=%s",
            translation,
            book,
            chapter,
        )
        raise BibleApiVerseNotFoundError(
            f"'{book} {chapter}' was not found in the '{translation}' translation. "
            "Please check the book name and chapter number."
        )

    if not response.ok:
        logger.warning(
            "Bible API non-200 response | status=%s url=%s",
            response.status_code,
            url,
        )
        raise BibleApiUnavailableError(
            f"The Bible API returned an unexpected status ({response.status_code}). "
            "Please try again later."
        )

    try:
        return response.json()
    except ValueError as exc:
        logger.error("Bible API returned non-JSON body | url=%s", url)
        raise BibleApiUnexpectedResponseError(
            "The Bible API returned an unreadable response. Please try again later."
        ) from exc


def _extract_verses(
    *,
    payload: dict,
    translation: str,
    book: str,
    chapter: int,
    verse_start: int,
    verse_end: int | None,
) -> list[dict]:
    """
    Pull the requested verse(s) out of a chapter payload.

    Parameters
    ----------
    payload : dict
        Parsed JSON from the Bible API chapter endpoint.
    translation : str
        Used only for error messages.
    book : str
        Used only for error messages.
    chapter : int
        Used only for error messages.
    verse_start : int
        First verse number to retrieve.
    verse_end : int | None
        Last verse number to retrieve, or ``None`` for a single verse.

    Returns
    -------
    list[dict]
        Ordered list of verse objects from the API response.
    """

    # ── Validate payload shape ──────────────────────────────────────────────

    if not isinstance(payload, dict) or "verses" not in payload:
        logger.error(
            "Bible API payload missing 'verses' key | translation=%s book=%s chapter=%s",
            translation,
            book,
            chapter,
        )
        raise BibleApiUnexpectedResponseError(
            "The Bible API returned a response in an unexpected format. "
            "Please try again later."
        )

    raw_verses: list = payload["verses"]

    if not isinstance(raw_verses, list):
        raise BibleApiUnexpectedResponseError(
            "The Bible API returned a response in an unexpected format. "
            "Please try again later."
        )

    # ── Index verses by their verse number ─────────────────────────────────

    verse_map: dict[int, dict] = {}

    for item in raw_verses:
        if not isinstance(item, dict):
            continue

        verse_number = item.get("verse") or item.get("verseNumber")

        if verse_number is None:
            continue

        try:
            verse_map[int(verse_number)] = item
        except (TypeError, ValueError):
            continue

    end = verse_end if verse_end is not None else verse_start
    requested_numbers = list(range(verse_start, end + 1))
    missing = [n for n in requested_numbers if n not in verse_map]

    if missing:
        missing_str = ", ".join(str(n) for n in missing)
        reference = _format_reference(book, chapter, verse_start, verse_end)
        logger.info(
            "Verse(s) not found in API response | reference=%s missing=%s",
            reference,
            missing_str,
        )

        raise BibleApiVerseNotFoundError(
            f"Verse(s) {missing_str} were not found in {book} {chapter} "
            f"({translation}). Please check the reference."
        )

    return [verse_map[n] for n in requested_numbers]


def _join_verse_texts(verses: list[dict]) -> str:
    """
    Extract and concatenate the text from an ordered list of verse objects.

    Parameters
    ----------
    verses : list[dict]
        Ordered list of verse dicts from the API response.

    Returns
    -------
    str
        Combined scripture text.
    """

    texts: list[str] = []

    for verse in verses:
        text = verse.get("text")

        if not isinstance(text, str) or not text.strip():
            raise BibleApiUnexpectedResponseError(
                "The Bible API returned verse data without text. "
                "Please try again later."
            )

        texts.append(text.strip())

    return " ".join(texts)


def _format_reference(
    book: str,
    chapter: int,
    verse_start: int,
    verse_end: int | None,
) -> str:
    """
    Format a human-readable Bible reference string.

    Parameters
    ----------
    book : str
        Name of the Bible book.
    chapter : int
        Chapter number.
    verse_start : int
        Starting verse number.
    verse_end : int | None
        Ending verse number, if provided.

    Returns
    -------
    str
        A formatted reference string like "Genesis 1:1" or "Genesis 1:1-3".
    """

    if verse_end is None or verse_end == verse_start:
        return f"{book} {chapter}:{verse_start}"

    return f"{book} {chapter}:{verse_start}-{verse_end}"
