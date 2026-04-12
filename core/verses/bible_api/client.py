"""
Responsible for all communication with the external Bible API.
"""

# python_packages
import logging

# third_party_packages
import requests

from decouple import config

# other_apps_packages
from core.verses.bible_api.exceptions import (
    BibleApiUnavailableError,
    BibleApiUnexpectedResponseError,
    BibleApiVerseNotFoundError,
)
from core.verses.choices import BibleVersionChoices


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
        Used for validation against the response and error messages.
    verse_start : int
        First verse number to retrieve.
    verse_end : int | None
        Last verse number to retrieve, or ``None`` for a single verse.

    Returns
    -------
    list[dict]
        Ordered list of verse dicts for the requested range, each with at
        least a ``"text"`` key.
    """

    # ── Bug 1 fix: validate payload shape BEFORE accessing nested keys ─────

    if not isinstance(payload, dict) or "chapter" not in payload:
        logger.error(
            "Bible API payload missing 'chapter' key | translation=%s book=%s chapter=%s",
            translation,
            book,
            chapter,
        )
        raise BibleApiUnexpectedResponseError(
            "The Bible API returned a response in an unexpected format. "
            "Please try again later."
        )

    payload_chapter = payload["chapter"]

    if not isinstance(payload_chapter, dict) or "content" not in payload_chapter:
        logger.error(
            "Bible API payload missing 'content' key | translation=%s book=%s chapter=%s",
            translation,
            book,
            chapter,
        )
        raise BibleApiUnexpectedResponseError(
            "The Bible API returned a response in an unexpected format. "
            "Please try again later."
        )

    payload_content = payload_chapter["content"]
    payload_chapter_number = payload_chapter.get("number")

    # ── Bug 2 fix: logger.error takes a plain string, not a tuple ──────────

    if chapter != payload_chapter_number:
        logger.error(
            "Bible API response chapter %s does not match the request chapter %s.",
            payload_chapter_number,
            chapter,
        )
        raise BibleApiUnexpectedResponseError(
            "The Bible API returned an unexpected response."
        )

    payload_version = payload.get("translation", {}).get("id", "")

    if payload_version == BibleVersionChoices.KJV.value:
        verse_map = process_kjv_verses(payload_content)
    else:
        verse_map = process_web_verses(payload_content)

    # ── Bug 4 fix: slice the map to the requested verse range ──────────────
    # ── Bug 3 fix: return a list[dict], not the raw dict ──────────────────

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


def process_web_verses(content: list[dict]) -> dict[int, dict]:
    """
    Process World English Bible (ENGWEBP) content into a verse-number-to-text mapping.

    Parameters
    ----------
    content : list[dict]
        List of verse items from the API chapter content.

    Returns
    -------
    dict[int, dict]
        Mapping of verse number to a dict containing the verse number and cleaned text.
    """

    verse_map: dict[int, dict] = {}

    for item in content:
        if not isinstance(item, dict):
            continue

        if item.get("type") != "verse":
            continue

        verse_number = item.get("number")

        if verse_number is None:
            continue

        try:
            raw_parts = item.get("content", [])

            if not isinstance(raw_parts, list):
                continue

            text_parts = [part for part in raw_parts if isinstance(part, str)]
            verse_text = " ".join(text_parts).strip()

            verse_map[int(verse_number)] = {
                "verse": verse_number,
                "text": verse_text,
            }

        except (TypeError, ValueError):
            continue

    return verse_map


def process_kjv_verses(content: list[dict]) -> dict[int, dict]:
    """
    Process King James Version (eng_kjv) content into a verse-number-to-text mapping.

    Parameters
    ----------
    content : list[dict]
        List of verse items from the API chapter content.

    Returns
    -------
    dict[int, dict]
        Mapping of verse number to a dict containing the verse number and text.
    """

    verse_map: dict[int, dict] = {}

    for item in content:
        if not isinstance(item, dict):
            continue

        if item.get("type") != "verse":
            continue

        verse_number = item.get("number")

        if verse_number is None:
            continue

        # ── Bug 5 fix: guard against missing/empty content before indexing ─

        raw_content = item.get("content")

        if not isinstance(raw_content, list) or not raw_content:
            continue

        verse_text = raw_content[0]

        if not isinstance(verse_text, str):
            continue

        try:
            verse_map[int(verse_number)] = {
                "verse": verse_number,
                "text": verse_text,
            }

        except (TypeError, ValueError):
            continue

    return verse_map
