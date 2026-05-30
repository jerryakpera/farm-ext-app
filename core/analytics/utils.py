"""
Utility functions for the analytics app.
"""

# python_packages
from datetime import date

# third_party_packages
from dateutil.relativedelta import relativedelta
from rest_framework.request import Request


def get_lga_filter(request: Request) -> int | None:
    """
    Extract and return the ?lga=<id> query parameter as an integer.

    Returns None if the parameter is absent or not a valid integer.

    Parameters
    ----------
    request : Request
        The incoming DRF request object.

    Returns
    -------
    int or None
        The LGA primary key, or None if not provided.
    """

    raw = request.query_params.get("lga")
    if raw is None:
        return None
    try:
        return int(raw)
    except (ValueError, TypeError):
        return None


def get_period_months(request: Request) -> int:
    """
    Extract and return the ?period=<months> query parameter.

    Defaults to 12. Clamps the value between 1 and 24.

    Parameters
    ----------
    request : Request
        The incoming DRF request object.

    Returns
    -------
    int
        Number of months to include in trend queries.
    """

    raw = request.query_params.get("period", "12")
    try:
        months = int(raw)
    except (ValueError, TypeError):
        months = 12
    return max(1, min(months, 24))


def period_start_date(months: int) -> date:
    """
    Return the first day of the month that is ``months`` months before today.

    Parameters
    ----------
    months : int
        Number of months to look back.

    Returns
    -------
    date
        The first day of the starting month.
    """

    today = date.today()
    return (today - relativedelta(months=months - 1)).replace(day=1)
