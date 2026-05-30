"""
Views for the analytics app — overview endpoint.

All analytics views inherit from AnalyticsView which parses the two global
query parameters once in initial() and exposes them as instance attributes:

    self.lga_id       — int | None  — from ?lga=<id>
    self.period_months — int        — from ?period=<months>, default 12, max 24
    self.period_start  — date       — first day of the period start month

Subclasses implement only get() and read those attributes directly.
"""

# third_party_packages
from rest_framework.request import Request
from rest_framework.response import Response

# other_apps_packages
from core.custom_user.models import User
from core.farms.models import Farm
from core.profiles.models import ExtensionAgentProfile
from core.visits.models.visit import Visit

# app_packages
from .analytics_view import AnalyticsView


class OverviewView(AnalyticsView):
    """
    GET /api/analytics/overview/.
    """

    def get(self, request: Request) -> Response:
        """
        Handle GET /api/analytics/overview/.

        Parameters
        ----------
        request : Request
            The incoming DRF request object.

        Returns
        -------
        Response
            JSON payload of platform-wide KPI counts.
        """

        total_farmers = User.objects.filter(role=User.Role.FARMER).count()
        total_farms = Farm.objects.count()
        total_agents = ExtensionAgentProfile.objects.count()
        total_visits = Visit.objects.count()
        verified_farms = Farm.objects.filter(is_verified=True).count()

        open_questions = 0
        advisory_posts = 0

        return Response(
            {
                "total_farmers": total_farmers,
                "total_farms": total_farms,
                "total_agents": total_agents,
                "total_visits": total_visits,
                "open_questions": open_questions,
                "advisory_posts": advisory_posts,
                "verified_farms": verified_farms,
            }
        )
