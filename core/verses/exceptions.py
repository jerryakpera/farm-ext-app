"""
Application-level exceptions for ``core.verse``.
"""


class VerseValidationError(Exception):
    """
    A business rule for verse creation or selection was violated.

    The message is safe to surface directly to the API client.
    """
