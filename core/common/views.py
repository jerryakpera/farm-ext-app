"""
Views for the common app.
"""

# django_packages
from django.db.models import Count, Q
from django.shortcuts import render

# third_party_packages
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# other_apps_packages
from core.advisory.models import AdvisoryPost
from core.farms.models import Farm
from core.profiles.models import ExtensionAgentProfile, FarmerProfile
from core.questions.models import Answer, Question

# app_packages
from .models import LGA, Ward
from .serializers import WardSerializer


def index_view(request):
    """
    Render the dashboard for the authenticated user.

    Farmers see stats and recent activity scoped to their own data.
    Extension agents see platform-wide stats and their own activity.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.

    Returns
    -------
    HttpResponse
        Rendered dashboard page.
    """

    if not request.user.is_authenticated:
        return render(
            request=request,
            template_name="common/pages/index.html",
            context={},
        )

    user = request.user
    context = {}

    recent_advisory_posts = (
        AdvisoryPost.objects.filter(is_published=True)
        .select_related("author__user")
        .prefetch_related("tags")
        .order_by("-published_at")[:3]
    )

    if user.is_farmer:
        farmer = user.farmer_profile

        my_questions = Question.objects.filter(farmer=farmer)
        my_farms = Farm.objects.filter(farmer=farmer).select_related(
            "lga", "primary_crop"
        )

        context = {
            "stats": {
                "farms": my_farms.count(),
                "questions": my_questions.count(),
                "open_questions": my_questions.filter(
                    status=Question.Status.OPEN
                ).count(),
                "answered_questions": my_questions.filter(
                    status=Question.Status.ANSWERED
                ).count(),
            },
            "recent_farms": my_farms.order_by("-created_at")[:4],
            "top_answers": (
                Answer.objects.filter(question__farmer=farmer)
                .annotate(
                    helpful_count=Count(
                        "helpfulness_ratings",
                        filter=Q(helpfulness_ratings__is_helpful=True),
                    )
                )
                .select_related("agent__user", "question")
                .order_by("-helpful_count")[:5]
            ),
            "recent_advisory_posts": recent_advisory_posts,
        }

    elif user.is_agent:
        agent = user.agent_profile

        my_answers = Answer.objects.filter(agent=agent)

        context = {
            "stats": {
                "total_farms": Farm.objects.count(),
                "total_farmers": FarmerProfile.objects.count(),
                "total_agents": ExtensionAgentProfile.objects.count(),
                "open_questions": Question.objects.filter(
                    status=Question.Status.OPEN
                ).count(),
                "total_questions": Question.objects.count(),
                "my_answers": my_answers.count(),
            },
            "recent_farms": (
                Farm.objects.select_related(
                    "farmer__user", "lga", "primary_crop"
                ).order_by("-created_at")[:4]
            ),
            "top_answers": (
                my_answers.annotate(
                    helpful_count=Count(
                        "helpfulness_ratings",
                        filter=Q(helpfulness_ratings__is_helpful=True),
                    )
                )
                .select_related("question")
                .order_by("-helpful_count")[:5]
            ),
            "recent_advisory_posts": recent_advisory_posts,
        }

    return render(
        request=request,
        template_name="dashboard/pages/index.html",
        context=context,
    )


class WardsByLGAView(APIView):
    """
    Return a list of wards belonging to a given LGA.
    """

    def get(self, request, lga_id, *args, **kwargs):
        """
        Handle GET requests.

        Parameters
        ----------
        request : Request
            The incoming DRF request.
        lga_id : int
            The primary key of the LGA.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Response
            A DRF Response containing the list of wards or an error message.
        """

        try:
            lga = LGA.objects.get(pk=lga_id)
        except LGA.DoesNotExist:
            return Response(
                {
                    "error": "LGA not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WardSerializer(
            lga.wards.order_by("name"),
            many=True,
        )

        return Response(
            {
                "wards": serializer.data,
            }
        )


class WardListView(APIView):
    """
    Return a list of all wards.
    """

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests.

        Parameters
        ----------
        request : Request
            The incoming DRF request.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Response
            A DRF Response containing all wards.
        """

        wards = Ward.objects.order_by("name")

        serializer = WardSerializer(wards, many=True)

        return Response(
            {
                "wards": serializer.data,
            }
        )
