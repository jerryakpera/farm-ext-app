"""
Tests for ``core.verses.bible_api.client``.
"""

# python_packages
from unittest.mock import MagicMock, patch

# third_party_packages
import pytest

# other_apps_packages
# local
from core.verses.bible_api.client import fetch_verse_text
from core.verses.bible_api.exceptions import (
    BibleApiUnavailableError,
    BibleApiUnexpectedResponseError,
    BibleApiVerseNotFoundError,
)


# ── Helpers & constants ───────────────────────────────────────────────────────

_PATCH_TARGET = "core.verses.bible_api.client.requests.get"

_TRANSLATION = "ENGWEBP"
_BOOK = "1John"
_CHAPTER = 4


def _make_response(
    *, status_code: int = 200, json_data: dict | None = None, raises=None
):
    """
    Build a mock ``requests.Response``.

    Parameters
    ----------
    status_code : int
        HTTP status code the mock response will report.
    json_data : dict | None
        Value returned by ``.json()``. Pass ``None`` to make ``.json()`` raise
        a ``ValueError`` (simulating a non-JSON body).
    raises : Exception | None
        If set, ``requests.get`` itself raises this exception instead of
        returning a response object.
    """

    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.ok = status_code < 400

    if json_data is not None:
        mock_resp.json.return_value = json_data
    else:
        mock_resp.json.side_effect = ValueError("No JSON")

    return mock_resp


def _chapter_payload(*verse_numbers: int) -> dict:
    """
    Build a minimal valid chapter payload containing the supplied verse numbers.

    Each verse gets a ``text`` value of ``"Verse {n} text."``.
    """

    return {"verses": [{"verse": n, "text": f"Verse {n} text."} for n in verse_numbers]}


# ── Happy-path tests ──────────────────────────────────────────────────────────


class TestFetchVerseTextSuccess:

    def test_single_verse_returns_correct_text(self):
        payload = _chapter_payload(19, 20)

        with patch(_PATCH_TARGET, return_value=_make_response(json_data=payload)):
            text = fetch_verse_text(
                translation=_TRANSLATION,
                book=_BOOK,
                chapter=_CHAPTER,
                verse_start=19,
            )

        assert text == "Verse 19 text."

    def test_two_verse_range_concatenates_with_space(self):
        payload = _chapter_payload(19, 20)

        with patch(_PATCH_TARGET, return_value=_make_response(json_data=payload)):
            text = fetch_verse_text(
                translation=_TRANSLATION,
                book=_BOOK,
                chapter=_CHAPTER,
                verse_start=19,
                verse_end=20,
            )

        assert text == "Verse 19 text. Verse 20 text."

    def test_three_verse_range_concatenates_correctly(self):
        payload = _chapter_payload(7, 8, 9)

        with patch(_PATCH_TARGET, return_value=_make_response(json_data=payload)):
            text = fetch_verse_text(
                translation=_TRANSLATION,
                book=_BOOK,
                chapter=_CHAPTER,
                verse_start=7,
                verse_end=9,
            )

        assert text == "Verse 7 text. Verse 8 text. Verse 9 text."

    def test_verse_end_equal_to_verse_start_treated_as_single(self):
        payload = _chapter_payload(19)

        with patch(_PATCH_TARGET, return_value=_make_response(json_data=payload)):
            text = fetch_verse_text(
                translation=_TRANSLATION,
                book=_BOOK,
                chapter=_CHAPTER,
                verse_start=19,
                verse_end=19,
            )

        assert text == "Verse 19 text."

    def test_correct_url_is_called(self):
        payload = _chapter_payload(1)

        with patch(
            _PATCH_TARGET, return_value=_make_response(json_data=payload)
        ) as mock_get:
            fetch_verse_text(
                translation="eng_kjv",
                book="Genesis",
                chapter=1,
                verse_start=1,
            )

        mock_get.assert_called_once_with(
            "https://bible.helloao.org/api/eng_kjv/Genesis/1.json",
            timeout=10,
        )

    def test_extra_verses_in_payload_do_not_affect_result(self):
        """Verses outside the requested range must be silently ignored."""
        payload = _chapter_payload(17, 18, 19, 20, 21)

        with patch(_PATCH_TARGET, return_value=_make_response(json_data=payload)):
            text = fetch_verse_text(
                translation=_TRANSLATION,
                book=_BOOK,
                chapter=_CHAPTER,
                verse_start=19,
                verse_end=20,
            )

        assert text == "Verse 19 text. Verse 20 text."

    def test_verse_text_is_stripped_of_surrounding_whitespace(self):
        payload = {"verses": [{"verse": 1, "text": "  In the beginning.  "}]}

        with patch(_PATCH_TARGET, return_value=_make_response(json_data=payload)):
            text = fetch_verse_text(
                translation=_TRANSLATION,
                book=_BOOK,
                chapter=1,
                verse_start=1,
            )

        assert text == "In the beginning."

    def test_api_called_only_once_per_request(self):
        payload = _chapter_payload(1, 2, 3)

        with patch(
            _PATCH_TARGET, return_value=_make_response(json_data=payload)
        ) as mock_get:
            fetch_verse_text(
                translation=_TRANSLATION,
                book=_BOOK,
                chapter=1,
                verse_start=1,
                verse_end=3,
            )

        assert mock_get.call_count == 1


# ── Network / availability error tests ───────────────────────────────────────


class TestFetchVerseTextNetworkErrors:

    def test_connection_error_raises_unavailable(self):
        # third_party_packages
        import requests as req

        with patch(_PATCH_TARGET, side_effect=req.exceptions.ConnectionError):
            with pytest.raises(BibleApiUnavailableError):
                fetch_verse_text(
                    translation=_TRANSLATION,
                    book=_BOOK,
                    chapter=_CHAPTER,
                    verse_start=19,
                )

    def test_timeout_raises_unavailable(self):
        # third_party_packages
        import requests as req

        with patch(_PATCH_TARGET, side_effect=req.exceptions.Timeout):
            with pytest.raises(BibleApiUnavailableError):
                fetch_verse_text(
                    translation=_TRANSLATION,
                    book=_BOOK,
                    chapter=_CHAPTER,
                    verse_start=19,
                )

    def test_generic_request_exception_raises_unavailable(self):
        # third_party_packages
        import requests as req

        with patch(_PATCH_TARGET, side_effect=req.exceptions.RequestException):
            with pytest.raises(BibleApiUnavailableError):
                fetch_verse_text(
                    translation=_TRANSLATION,
                    book=_BOOK,
                    chapter=_CHAPTER,
                    verse_start=19,
                )

    def test_404_response_raises_verse_not_found(self):
        with patch(
            _PATCH_TARGET, return_value=_make_response(status_code=404, json_data={})
        ):
            with pytest.raises(BibleApiVerseNotFoundError):
                fetch_verse_text(
                    translation=_TRANSLATION,
                    book=_BOOK,
                    chapter=_CHAPTER,
                    verse_start=19,
                )

    def test_500_response_raises_unavailable(self):
        with patch(
            _PATCH_TARGET, return_value=_make_response(status_code=500, json_data={})
        ):
            with pytest.raises(BibleApiUnavailableError):
                fetch_verse_text(
                    translation=_TRANSLATION,
                    book=_BOOK,
                    chapter=_CHAPTER,
                    verse_start=19,
                )

    def test_non_json_response_raises_unexpected_response(self):
        # json_data=None makes mock_resp.json() raise ValueError
        with patch(
            _PATCH_TARGET, return_value=_make_response(status_code=200, json_data=None)
        ):
            with pytest.raises(BibleApiUnexpectedResponseError):
                fetch_verse_text(
                    translation=_TRANSLATION,
                    book=_BOOK,
                    chapter=_CHAPTER,
                    verse_start=19,
                )

    def test_unavailable_error_message_is_user_friendly(self):
        # third_party_packages
        import requests as req

        with patch(_PATCH_TARGET, side_effect=req.exceptions.ConnectionError):
            with pytest.raises(BibleApiUnavailableError) as exc_info:
                fetch_verse_text(
                    translation=_TRANSLATION,
                    book=_BOOK,
                    chapter=_CHAPTER,
                    verse_start=19,
                )

        assert "try again" in str(exc_info.value).lower()


# ── Payload shape error tests ─────────────────────────────────────────────────


class TestFetchVerseTextUnexpectedPayload:

    def test_missing_verses_key_raises_unexpected_response(self):
        payload = {"data": []}  # 'verses' key absent

        with patch(_PATCH_TARGET, return_value=_make_response(json_data=payload)):
            with pytest.raises(BibleApiUnexpectedResponseError):
                fetch_verse_text(
                    translation=_TRANSLATION,
                    book=_BOOK,
                    chapter=_CHAPTER,
                    verse_start=19,
                )

    def test_verses_not_a_list_raises_unexpected_response(self):
        payload = {"verses": "not a list"}

        with patch(_PATCH_TARGET, return_value=_make_response(json_data=payload)):
            with pytest.raises(BibleApiUnexpectedResponseError):
                fetch_verse_text(
                    translation=_TRANSLATION,
                    book=_BOOK,
                    chapter=_CHAPTER,
                    verse_start=19,
                )

    def test_verse_object_missing_text_raises_unexpected_response(self):
        payload = {"verses": [{"verse": 19}]}  # no 'text' key

        with patch(_PATCH_TARGET, return_value=_make_response(json_data=payload)):
            with pytest.raises(BibleApiUnexpectedResponseError):
                fetch_verse_text(
                    translation=_TRANSLATION,
                    book=_BOOK,
                    chapter=_CHAPTER,
                    verse_start=19,
                )

    def test_payload_is_a_list_not_dict_raises_unexpected_response(self):
        with patch(_PATCH_TARGET, return_value=_make_response(json_data=[])):
            with pytest.raises(BibleApiUnexpectedResponseError):
                fetch_verse_text(
                    translation=_TRANSLATION,
                    book=_BOOK,
                    chapter=_CHAPTER,
                    verse_start=19,
                )


# ── Verse not found tests ─────────────────────────────────────────────────────


class TestFetchVerseTextVerseNotFound:

    def test_single_verse_absent_raises_verse_not_found(self):
        payload = _chapter_payload(1, 2, 3)  # verse 19 not present

        with patch(_PATCH_TARGET, return_value=_make_response(json_data=payload)):
            with pytest.raises(BibleApiVerseNotFoundError):
                fetch_verse_text(
                    translation=_TRANSLATION,
                    book=_BOOK,
                    chapter=_CHAPTER,
                    verse_start=19,
                )

    def test_partial_range_missing_raises_verse_not_found(self):
        payload = _chapter_payload(19)  # verse 20 not present

        with patch(_PATCH_TARGET, return_value=_make_response(json_data=payload)):
            with pytest.raises(BibleApiVerseNotFoundError):
                fetch_verse_text(
                    translation=_TRANSLATION,
                    book=_BOOK,
                    chapter=_CHAPTER,
                    verse_start=19,
                    verse_end=20,
                )

    def test_empty_verses_list_raises_verse_not_found(self):
        payload = {"verses": []}

        with patch(_PATCH_TARGET, return_value=_make_response(json_data=payload)):
            with pytest.raises(BibleApiVerseNotFoundError):
                fetch_verse_text(
                    translation=_TRANSLATION,
                    book=_BOOK,
                    chapter=_CHAPTER,
                    verse_start=19,
                )

    def test_verse_not_found_error_message_is_user_friendly(self):
        payload = {"verses": []}

        with patch(_PATCH_TARGET, return_value=_make_response(json_data=payload)):
            with pytest.raises(BibleApiVerseNotFoundError) as exc_info:
                fetch_verse_text(
                    translation=_TRANSLATION,
                    book=_BOOK,
                    chapter=_CHAPTER,
                    verse_start=19,
                )

        message = str(exc_info.value).lower()
        assert "1john" in message or "not found" in message

    def test_supports_versenumber_key_as_fallback(self):
        """API may use ``verseNumber`` instead of ``verse``."""
        payload = {"verses": [{"verseNumber": 19, "text": "We love."}]}

        with patch(_PATCH_TARGET, return_value=_make_response(json_data=payload)):
            text = fetch_verse_text(
                translation=_TRANSLATION,
                book=_BOOK,
                chapter=_CHAPTER,
                verse_start=19,
            )

        assert text == "We love."
