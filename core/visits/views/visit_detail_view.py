"""
Views for the visits app.
"""

# django_packages
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

# other_apps_packages
from core.profiles.decorators import agent_required

# app_packages
from ..models import Visit


@agent_required
def visit_detail_view(request, pk):
    """
    Display a single visit and all child records accumulated against it.

    Fetches the Visit and every related child model in a single
    database round-trip using select_related and prefetch_related.
    Each crop analysis is prefetched with its own issues, actions, and
    pest incidences. Each livestock analysis is prefetched with its own
    issues, actions, and disease incidences.

    Access is restricted to the agent who logged the visit and
    superusers. Any other authenticated agent is redirected to their
    visit list with an error message.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    pk : int
        The primary key of the visit to display.

    Returns
    -------
    HttpResponse
        Rendered visit detail page or redirect if access is denied.
    """

    visit = get_object_or_404(
        Visit.objects.select_related(
            "agent__user",
            "farm__farmer__user",
            "farm__lga",
        ).prefetch_related(
            "issues",
            "crop_analyses__crop",
            "crop_analyses__variety",
            "crop_analyses__issues",
            "crop_analyses__actions",
            "crop_analyses__pest_incidences",
            "livestock_analyses__animal",
            "livestock_analyses__issues",
            "livestock_analyses__actions",
            "livestock_analyses__disease_incidences",
        ),
        pk=pk,
    )

    is_owner = visit.agent == request.user.agent_profile

    if not is_owner and not request.user.is_superuser:
        messages.error(request, "You are not authorised to view this visit.")
        return redirect("visits:list")

    # farmer_feedback is a OneToOneField — accessing it raises
    # RelatedObjectDoesNotExist when no feedback has been recorded yet.
    # Normalise this to None so the template can branch cleanly.
    try:
        farmer_feedback = visit.farmer_feedback
    except Visit.farmer_feedback.RelatedObjectDoesNotExist:
        farmer_feedback = None

    show_verify_button = (
        visit.purpose == Visit.VisitPurpose.FARM_VERIFICATION
        and not visit.farm.is_verified
    )

    context = {
        "visit": visit,
        "farmer_feedback": farmer_feedback,
        "is_owner": is_owner,
        "show_verify_button": show_verify_button,
        "crop_analyses": visit.crop_analyses.all(),
        "livestock_analyses": visit.livestock_analyses.all(),
        "visit_issues": visit.issues.all(),
    }

    return render(
        request=request,
        template_name="visits/pages/visit_detail_page.html",
        context=context,
    )
