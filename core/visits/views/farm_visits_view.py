"""
Views for the visits app.
"""

# django_packages
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

# other_apps_packages
from core.farms.models import Farm
from core.profiles.decorators import agent_required

# app_packages
from ..constants import VISIT_EDIT_WINDOW_HOURS
from ..models import Visit


@agent_required
def farm_visits_view(request, farm_pk):
    """
    Display all visits recorded for a specific farm.

    Accessible from the farm detail page. Access is granted to any
    agent who either logged at least one visit to this farm or is
    assigned to the farm's LGA. All other agents are redirected to
    their visit list with an error message.

    Results are ordered by most recent visit first and paginated at
    20 visits per page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    farm_pk : int
        The primary key of the farm whose visits are being listed.

    Returns
    -------
    HttpResponse
        Rendered farm visits page or redirect if access is denied.
    """

    # django_packages
    from django.core.paginator import Paginator

    agent = request.user.agent_profile

    farm = get_object_or_404(
        Farm.objects.select_related("lga", "farmer__user"),
        pk=farm_pk,
    )

    is_assigned_to_lga = agent.assigned_lgas.filter(pk=farm.lga_id).exists()
    has_visited_farm = Visit.objects.filter(agent=agent, farm=farm).exists()

    if (
        not is_assigned_to_lga
        and not has_visited_farm
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "You are not authorised to view visits for this farm.",
        )
        return redirect("visits:list")

    visits = (
        Visit.objects.filter(farm=farm)
        .select_related("agent__user", "farm__lga")
        .order_by("-visit_date", "-visit_time")
    )

    paginator = Paginator(visits, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "farm": farm,
        "page_obj": page_obj,
    }

    return render(
        request=request,
        template_name="visits/pages/farm_visits.html",
        context=context,
    )
