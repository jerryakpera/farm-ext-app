"""
Views for the common app.
"""

# django_packages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render

# other_apps_packages
from core.farms.models import Farm
from core.profiles.models import ExtensionAgentProfile, FarmerProfile
from core.questions.models import Answer, Question


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
        }

    return render(
        request=request,
        template_name="dashboard/pages/index.html",
        context=context,
    )
