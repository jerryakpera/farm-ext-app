"""
Utility functions for the `verses` app.
"""

# app_packages
from .choices import BibleBookChoices


def get_book_label(book: str) -> str:
    """
    Return human-readable Bible book name from its code.

    Parameters
    ----------
    book : str
        The Bible book code.

    Returns
    -------
    str
        Returns the human readable book name.
    """

    try:
        return BibleBookChoices(book).label
    except ValueError:
        return book
