"""
Application-level exceptions for Bible API failures.
"""


class BibleApiError(Exception):
    """
    Base class for all Bible API client errors.
    """


class BibleApiUnavailableError(BibleApiError):
    """
    The remote Bible API could not be reached or returned a non-200 status.
    """


class BibleApiUnexpectedResponseError(BibleApiError):
    """
    The API responded successfully but the payload did not match expectations.
    """


class BibleApiVerseNotFoundError(BibleApiError):
    """
    The chapter was retrieved but the requested verse(s) were not present.
    """
