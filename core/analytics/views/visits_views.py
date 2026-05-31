"""
Views for the analytics app — section 7.4: Visits.
"""

# django_packages
from django.db.models import Count, Value
from django.db.models.functions import Concat, TruncMonth

# third_party_packages
from rest_framework.request import Request
from rest_framework.response import Response

# other_apps_packages
from core.visits.models.visit import Visit

# app_packages
from .analytics_view import AnalyticsView


class VisitsByPurposeView(AnalyticsView):
    """
    GET /api/analytics/visits/by-purpose/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/visits/by-purpose/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of purpose keys, labels, and counts.
        """

        qs = Visit.objects.all()

        if self.lga_id:
            qs = qs.filter(farm__lga_id=self.lga_id)

        rows = qs.values("purpose").annotate(count=Count("id")).order_by("-count")

        label_map = dict(Visit.VisitPurpose.choices)

        return Response(
            [
                {
                    "purpose": row["purpose"],
                    "label": label_map.get(row["purpose"], row["purpose"]),
                    "count": row["count"],
                }
                for row in rows
            ]
        )


class VisitsByOutcomeView(AnalyticsView):
    """
    GET /api/analytics/visits/by-outcome/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/visits/by-outcome/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of outcome keys, labels, and counts.
        """

        qs = Visit.objects.exclude(outcome="")

        if self.lga_id:
            qs = qs.filter(farm__lga_id=self.lga_id)

        rows = qs.values("outcome").annotate(count=Count("id")).order_by("-count")

        label_map = dict(Visit.VisitOutcome.choices)

        return Response(
            [
                {
                    "outcome": row["outcome"],
                    "label": label_map.get(row["outcome"], row["outcome"]),
                    "count": row["count"],
                }
                for row in rows
            ]
        )


class VisitTrendView(AnalyticsView):
    """
    GET /api/analytics/visits/trend/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/visits/trend/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of month labels and visit counts.
        """

        qs = Visit.objects.filter(visit_date__gte=self.period_start)

        if self.lga_id:
            qs = qs.filter(farm__lga_id=self.lga_id)

        rows = (
            qs.annotate(period=TruncMonth("visit_date"))
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


class VisitsByAgentView(AnalyticsView):
    """
    GET /api/analytics/visits/by-agent/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/visits/by-agent/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of agent names, staff IDs, and visit counts (top 10).
        """

        qs = Visit.objects.all()

        if self.lga_id:
            qs = qs.filter(farm__lga_id=self.lga_id)

        rows = (
            qs.annotate(
                agent_name=Concat(
                    "agent__user__first_name",
                    Value(" "),
                    "agent__user__last_name",
                ),
            )
            .values("agent_name", "agent__staff_id")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        return Response(
            [
                {
                    "agent_name": row["agent_name"],
                    "staff_id": row["agent__staff_id"],
                    "count": row["count"],
                }
                for row in rows
            ]
        )


class VisitsByLgaView(AnalyticsView):
    """
    GET /api/analytics/visits/by-lga/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/visits/by-lga/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of LGA names and visit counts.
        """

        qs = Visit.objects.filter(
            farm__isnull=False,
            farm__lga__isnull=False,
        )

        if self.lga_id:
            qs = qs.filter(farm__lga_id=self.lga_id)

        rows = (
            qs.values("farm__lga__name").annotate(count=Count("id")).order_by("-count")
        )

        return Response(
            [{"lga": row["farm__lga__name"], "count": row["count"]} for row in rows]
        )


class VisitFollowUpRateView(AnalyticsView):
    """
    GET /api/analytics/visits/follow-up-rate/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/visits/follow-up-rate/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list with follow-up required and not-required counts.
        """

        qs = Visit.objects.all()

        if self.lga_id:
            qs = qs.filter(farm__lga_id=self.lga_id)

        required = qs.filter(follow_up_required=True).count()
        not_required = qs.filter(follow_up_required=False).count()

        return Response(
            [
                {"label": "Follow-up Required", "count": required},
                {"label": "No Follow-up Needed", "count": not_required},
            ]
        )


class VisitsByPriorityView(AnalyticsView):
    """
    GET /api/analytics/visits/priority-level/.
    """

    # Fixed display order for priority levels.
    _PRIORITY_ORDER = [
        Visit.PriorityLevel.LOW,
        Visit.PriorityLevel.MEDIUM,
        Visit.PriorityLevel.HIGH,
    ]

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/visits/priority-level/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of priority keys, labels, and counts in severity order.
        """

        qs = Visit.objects.all()

        if self.lga_id:
            qs = qs.filter(farm__lga_id=self.lga_id)

        counts = dict(
            qs.values("priority_level")
            .annotate(count=Count("id"))
            .values_list("priority_level", "count")
        )

        label_map = dict(Visit.PriorityLevel.choices)

        return Response(
            [
                {
                    "priority": level,
                    "label": label_map[level],
                    "count": counts.get(level, 0),
                }
                for level in self._PRIORITY_ORDER
            ]
        )
