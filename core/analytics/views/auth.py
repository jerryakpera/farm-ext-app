"""
Authentication views for the analytics app.
"""

# third_party_packages
from rest_framework.response import Response
from rest_framework.views import APIView

# app_packages
from ..models import DashboardWhitelist
from ..serializers import DashboardWhitelistCheckSerializer


class DashboardAuthCheckView(APIView):
    """
    Check whether a given email is permitted to access the dashboard.

    Accepts a single query parameter `email` and checks it against the
    DashboardWhitelist. Returns an allowed or denied response with no
    token exchange or session creation.
    """

    def get(self, request):
        """
        Handle GET /api/analytics/auth/check/?email=<email>.

        Parameters
        ----------
        request : Request
            DRF request object. Expected query param: ?email=<email>.

        Returns
        -------
        Response
            200 with ``{"allowed": true}`` if the email is whitelisted.
            200 with ``{"allowed": false, "reason": "..."}`` if not whitelisted
            or if the query parameter is missing or invalid.
        """

        serializer = DashboardWhitelistCheckSerializer(data=request.query_params)

        if not serializer.is_valid():
            return Response(
                {"allowed": False, "reason": "Invalid or missing email parameter."}
            )

        email = serializer.validated_data["email"]
        is_allowed = DashboardWhitelist.objects.filter(email__iexact=email).exists()

        if not is_allowed:
            return Response(
                {
                    "allowed": False,
                    "reason": "This email is not authorised to access the dashboard.",
                }
            )

        return Response({"allowed": True})
