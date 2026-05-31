"""
Views for the analytics app — section 7.6: Advisory Posts.
"""

# django_packages
from django.db.models import Count
from django.db.models.functions import TruncMonth

# third_party_packages
from rest_framework.request import Request
from rest_framework.response import Response

# other_apps_packages
from core.advisory.models import AdvisoryPost

# app_packages
from .analytics_view import AnalyticsView


class AdvisoryByTypeView(AnalyticsView):
    """
    GET /api/analytics/advisory/by-type/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/advisory/by-type/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of post type keys, labels, and counts.
        """

        rows = (
            AdvisoryPost.objects.values("post_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        label_map = dict(AdvisoryPost.PostType.choices)

        return Response(
            [
                {
                    "post_type": row["post_type"],
                    "label": label_map.get(row["post_type"], row["post_type"]),
                    "count": row["count"],
                }
                for row in rows
            ]
        )


class AdvisoryPublishedVsDraftView(AnalyticsView):
    """
    GET /api/analytics/advisory/published-vs-draft/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/advisory/published-vs-draft/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list with published and draft post counts.
        """

        published = AdvisoryPost.objects.filter(is_published=True).count()
        draft = AdvisoryPost.objects.filter(is_published=False).count()

        return Response(
            [
                {"status": "Published", "count": published},
                {"status": "Draft", "count": draft},
            ]
        )


class AdvisoryTrendView(AnalyticsView):
    """
    GET /api/analytics/advisory/trend/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/advisory/trend/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of month labels and published post counts.
        """

        rows = (
            AdvisoryPost.objects.filter(
                is_published=True,
                published_at__date__gte=self.period_start,
            )
            .annotate(period=TruncMonth("published_at"))
            .values("period")
            .annotate(count=Count("id"))
            .order_by("period")
        )

        return Response(
            [
                {
                    "month": row["period"].strftime("%b %Y"),
                    "count": row["count"],
                }
                for row in rows
            ]
        )
