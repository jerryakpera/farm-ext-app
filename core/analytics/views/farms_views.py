"""
Views for the analytics app — section 7.3: Farmers & Farms.
"""

# django_packages
from django.db.models import Count
from django.db.models.functions import TruncMonth

# third_party_packages
from rest_framework.request import Request
from rest_framework.response import Response

# other_apps_packages
from core.farms.models import Farm
from core.profiles.models import FarmerProfile

# app_packages
from .analytics_view import AnalyticsView


class FarmersByLgaView(AnalyticsView):
    """
    GET /api/analytics/farmers/by-lga/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/farmers/by-lga/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of LGA names and farmer counts.
        """

        qs = FarmerProfile.objects.filter(lga__isnull=False)

        if self.lga_id:
            qs = qs.filter(lga_id=self.lga_id)

        rows = qs.values("lga__name").annotate(count=Count("id")).order_by("-count")

        return Response(
            [{"lga": row["lga__name"], "count": row["count"]} for row in rows]
        )


class FarmsByLgaView(AnalyticsView):
    """
    GET /api/analytics/farms/by-lga/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/farms/by-lga/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of LGA names and farm counts.
        """

        qs = Farm.objects.filter(lga__isnull=False)

        if self.lga_id:
            qs = qs.filter(lga_id=self.lga_id)

        rows = qs.values("lga__name").annotate(count=Count("id")).order_by("-count")

        return Response(
            [{"lga": row["lga__name"], "count": row["count"]} for row in rows]
        )


class FarmVerificationStatusView(AnalyticsView):
    """
    GET /api/analytics/farms/verification-status/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/farms/verification-status/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list with verified and unverified farm counts.
        """

        qs = Farm.objects.all()

        if self.lga_id:
            qs = qs.filter(lga_id=self.lga_id)

        verified = qs.filter(is_verified=True).count()
        unverified = qs.filter(is_verified=False).count()

        return Response(
            [
                {"status": "Verified", "count": verified},
                {"status": "Unverified", "count": unverified},
            ]
        )


class FarmsPrimaryCropsView(AnalyticsView):
    """
    GET /api/analytics/farms/primary-crops/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/farms/primary-crops/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of crop names and farm counts.
        """

        qs = Farm.objects.filter(primary_crop__isnull=False)

        if self.lga_id:
            qs = qs.filter(lga_id=self.lga_id)

        rows = (
            qs.values("primary_crop__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return Response(
            [{"crop": row["primary_crop__name"], "count": row["count"]} for row in rows]
        )


class FarmsRegistrationTrendView(AnalyticsView):
    """
    GET /api/analytics/farms/registration-trend/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/farms/registration-trend/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of month labels and farm registration counts.
        """

        qs = Farm.objects.filter(created_at__date__gte=self.period_start)

        if self.lga_id:
            qs = qs.filter(lga_id=self.lga_id)

        rows = (
            qs.annotate(period=TruncMonth("created_at"))
            .values("period")
            .annotate(count=Count("id"))
            .order_by("period")
        )

        data = [
            {
                "month": row["period"].strftime("%b %Y"),
                "count": row["count"],
            }
            for row in rows
        ]

        return Response(data)


class FarmsRecentView(AnalyticsView):
    """
    GET /api/analytics/farms/recent/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/farms/recent/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of the most recently registered farms.
        """

        try:
            limit = min(int(request.query_params.get("limit", 5)), 20)
        except (ValueError, TypeError):
            limit = 5

        farms = Farm.objects.select_related("farmer__user", "lga").order_by(
            "-created_at"
        )[:limit]

        return Response(
            [
                {
                    "id": farm.id,
                    "name": farm.name,
                    "lga": farm.lga.name if farm.lga else None,
                    "farmer_name": (
                        f"{farm.farmer.user.first_name} "
                        f"{farm.farmer.user.last_name}".strip()
                    ),
                    "registered_at": farm.created_at.date().isoformat(),
                }
                for farm in farms
            ]
        )
