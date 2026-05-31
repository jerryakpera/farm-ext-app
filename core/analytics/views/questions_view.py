"""
Views for the analytics app — section 7.5: Questions & Answers.
"""

# django_packages
from django.db.models import Count
from django.db.models.functions import TruncMonth

# third_party_packages
from rest_framework.request import Request
from rest_framework.response import Response

# other_apps_packages
from core.questions.models import Answer, AnswerHelpfulness, Question

# app_packages
from .analytics_view import AnalyticsView


class QuestionsByStatusView(AnalyticsView):
    """
    GET /api/analytics/questions/by-status/.
    """

    _STATUS_ORDER = [
        Question.Status.OPEN,
        Question.Status.ANSWERED,
        Question.Status.ESCALATED,
        Question.Status.CLOSED,
    ]

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/questions/by-status/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of status keys, labels, and counts in display order.
        """

        qs = Question.objects.all()

        if self.lga_id:
            qs = qs.filter(farm__lga_id=self.lga_id)

        counts = dict(
            qs.values("status")
            .annotate(count=Count("id"))
            .values_list("status", "count")
        )

        label_map = dict(Question.Status.choices)

        return Response(
            [
                {
                    "status": status,
                    "label": label_map[status],
                    "count": counts.get(status, 0),
                }
                for status in self._STATUS_ORDER
            ]
        )


class QuestionTrendView(AnalyticsView):
    """
    GET /api/analytics/questions/trend/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/questions/trend/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of month labels and question counts.
        """

        qs = Question.objects.filter(created_at__date__gte=self.period_start)

        if self.lga_id:
            qs = qs.filter(farm__lga_id=self.lga_id)

        rows = (
            qs.annotate(period=TruncMonth("created_at"))
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


class QuestionEscalationRateView(AnalyticsView):
    """
    GET /api/analytics/questions/escalation-rate/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/questions/escalation-rate/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON object with total, escalated count, and rate percentage.
        """

        qs = Question.objects.all()

        if self.lga_id:
            qs = qs.filter(farm__lga_id=self.lga_id)

        total = qs.count()
        escalated = qs.filter(is_escalated=True).count()
        rate = round((escalated / total * 100), 1) if total > 0 else 0.0

        return Response(
            {
                "total": total,
                "escalated": escalated,
                "escalation_rate_pct": rate,
            }
        )


class AnswerHelpfulnessView(AnalyticsView):
    """
    GET /api/analytics/questions/answer-helpfulness/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/questions/answer-helpfulness/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list with helpful and not-helpful rating counts.
        """

        helpful = AnswerHelpfulness.objects.filter(is_helpful=True).count()
        not_helpful = AnswerHelpfulness.objects.filter(is_helpful=False).count()

        return Response(
            [
                {"label": "Helpful", "count": helpful},
                {"label": "Not Helpful", "count": not_helpful},
            ]
        )


class TopCropsByQuestionsView(AnalyticsView):
    """
    GET /api/analytics/questions/top-crops/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/questions/top-crops/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of crop names and question counts (top 10).
        """

        qs = Question.objects.filter(crop_concern__isnull=False)

        if self.lga_id:
            qs = qs.filter(farm__lga_id=self.lga_id)

        rows = (
            qs.values("crop_concern__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        return Response(
            [{"crop": row["crop_concern__name"], "count": row["count"]} for row in rows]
        )
