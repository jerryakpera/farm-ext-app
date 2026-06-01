"""
Views for the analytics app — section 7.8: Geographic / Heatmap.
"""

# django_packages
from django.db.models import Count, OuterRef, Subquery

# third_party_packages
from rest_framework.request import Request
from rest_framework.response import Response

# other_apps_packages
from core.common.models import LGA, Ward
from core.farms.models import Farm
from core.profiles.models import FarmerProfile
from core.questions.models import Question
from core.visits.models.crop_issue import CropIssue
from core.visits.models.visit import Visit

# app_packages
from .analytics_view import AnalyticsView


class GeoFarmersByLgaView(AnalyticsView):
    """
    GET /api/analytics/geo/farmers-by-lga/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/geo/farmers-by-lga/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of LGA rows with farmer, farm, and visit counts.
        """

        lgas = LGA.objects.all().order_by("name")

        # Build lookup dicts keyed by lga_id for O(n) assembly
        farmer_counts = dict(
            FarmerProfile.objects.filter(lga__isnull=False)
            .values("lga_id")
            .annotate(n=Count("id"))
            .values_list("lga_id", "n")
        )

        farm_counts = dict(
            Farm.objects.filter(lga__isnull=False)
            .values("lga_id")
            .annotate(n=Count("id"))
            .values_list("lga_id", "n")
        )

        visit_counts = dict(
            Visit.objects.filter(farm__lga__isnull=False)
            .values("farm__lga_id")
            .annotate(n=Count("id"))
            .values_list("farm__lga_id", "n")
        )

        return Response(
            [
                {
                    "lga": lga.name,
                    "lga_id": lga.id,
                    "farmer_count": farmer_counts.get(lga.id, 0),
                    "farm_count": farm_counts.get(lga.id, 0),
                    "visit_count": visit_counts.get(lga.id, 0),
                }
                for lga in lgas
            ]
        )


class GeoFarmersByWardView(AnalyticsView):
    """
    GET /api/analytics/geo/farmers-by-ward/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/geo/farmers-by-ward/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of ward rows with parent LGA and aggregate counts.
        """

        # Counts per LGA (same lookups as GeoFarmersByLgaView)
        farmer_counts_by_lga = dict(
            FarmerProfile.objects.filter(lga__isnull=False)
            .values("lga_id")
            .annotate(n=Count("id"))
            .values_list("lga_id", "n")
        )

        farm_counts_by_lga = dict(
            Farm.objects.filter(lga__isnull=False)
            .values("lga_id")
            .annotate(n=Count("id"))
            .values_list("lga_id", "n")
        )

        visit_counts_by_lga = dict(
            Visit.objects.filter(farm__lga__isnull=False)
            .values("farm__lga_id")
            .annotate(n=Count("id"))
            .values_list("farm__lga_id", "n")
        )

        # Wards per LGA — needed to proportionally distribute LGA counts
        ward_counts_by_lga: dict[int, int] = {}
        for ward in Ward.objects.select_related("lga").all():
            ward_counts_by_lga[ward.lga_id] = ward_counts_by_lga.get(ward.lga_id, 0) + 1

        wards = Ward.objects.select_related("lga").order_by("lga__name", "name")

        rows = []
        for ward in wards:
            lga_id = ward.lga_id
            ward_count = ward_counts_by_lga.get(lga_id, 1)

            # Distribute LGA totals equally across its wards (integer division)
            farmer_count = farmer_counts_by_lga.get(lga_id, 0) // ward_count
            farm_count = farm_counts_by_lga.get(lga_id, 0) // ward_count
            visit_count = visit_counts_by_lga.get(lga_id, 0) // ward_count

            rows.append(
                {
                    "ward": ward.name,
                    "lga": ward.lga.name,
                    "ward_id": ward.id,
                    "farmer_count": farmer_count,
                    "farm_count": farm_count,
                    "visit_count": visit_count,
                }
            )

        return Response(rows)


class GeoQuestionsByLgaView(AnalyticsView):
    """
    GET /api/analytics/geo/questions-by-lga/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/geo/questions-by-lga/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of LGA rows with question and escalation counts.
        """

        lgas = LGA.objects.all().order_by("name")

        question_counts = dict(
            Question.objects.filter(farm__lga__isnull=False)
            .values("farm__lga_id")
            .annotate(n=Count("id"))
            .values_list("farm__lga_id", "n")
        )

        escalation_counts = dict(
            Question.objects.filter(
                farm__lga__isnull=False,
                is_escalated=True,
            )
            .values("farm__lga_id")
            .annotate(n=Count("id"))
            .values_list("farm__lga_id", "n")
        )

        return Response(
            [
                {
                    "lga": lga.name,
                    "lga_id": lga.id,
                    "question_count": question_counts.get(lga.id, 0),
                    "escalation_count": escalation_counts.get(lga.id, 0),
                }
                for lga in lgas
            ]
        )


class GeoCropIssuesByLgaView(AnalyticsView):
    """
    GET /api/analytics/geo/crop-issues-by-lga/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/geo/crop-issues-by-lga/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON list of LGA rows with the top crop issue label.
        """

        lgas = LGA.objects.all().order_by("name")

        # Get the most common issue_type per LGA using a subquery
        # CropIssue → analysis (VisitCropAnalysis) → visit → farm → lga
        top_issue_qs = (
            CropIssue.objects.filter(analysis__visit__farm__lga=OuterRef("pk"))
            .values("analysis__visit__farm__lga")
            .annotate(n=Count("id"))
            .order_by("analysis__visit__farm__lga", "-n")
            .values("issue_type")[:1]
        )

        lgas_with_issue = lgas.annotate(top_issue_type=Subquery(top_issue_qs))

        label_map = dict(CropIssue.IssueType.choices)

        return Response(
            [
                {
                    "lga": lga.name,
                    "lga_id": lga.id,
                    "top_crop_issue": (
                        label_map.get(lga.top_issue_type)
                        if lga.top_issue_type
                        else None
                    ),
                    "top_crop_issue_key": lga.top_issue_type,
                }
                for lga in lgas_with_issue
            ]
        )
