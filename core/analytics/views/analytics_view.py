"""
AnalyticsView Base for the analytics app.
"""

# third_party_packages
from rest_framework.request import Request
from rest_framework.views import APIView

# app_packages
from ..utils import get_lga_filter, get_period_months, period_start_date


class AnalyticsView(APIView):
    """
    Base class for all analytics endpoints.

    Parses the two global query parameters once in initial() and exposes them
    as instance attributes so subclasses do not repeat the calls:

        self.lga_id        — int | None
        self.period_months — int
        self.period_start  — date
    """

    def initial(self, request: Request, *args, **kwargs) -> None:
        """
        Run standard APIView setup then parse shared query parameters.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.
        *args
            Passed through to the parent.
        **kwargs
            Passed through to the parent.
        """

        super().initial(request, *args, **kwargs)
        self.lga_id = get_lga_filter(request)
        self.period_months = get_period_months(request)
        self.period_start = period_start_date(self.period_months)
