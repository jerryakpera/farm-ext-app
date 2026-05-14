"""
Views for the visits app.
"""

# django_packages
from django.shortcuts import render

# other_apps_packages
from core.farms.models import Farm
from core.profiles.decorators import agent_required

# app_packages
from ..constants import VISIT_EDIT_WINDOW_HOURS
from ..models import Visit


@agent_required
def visit_list_view(request):
    """
    Display all visits logged by the authenticated extension agent,
    with optional filtering by date range, purpose, farm, and priority
    level.

    Filters are read from GET parameters and applied incrementally to
    the base queryset. Invalid or missing filter values are silently
    ignored so the view always returns a valid page.

    Results are paginated at 20 visits per page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request. The following GET parameters are
        recognised:
        - ``date_from`` (YYYY-MM-DD) — lower bound for visit_date
        - ``date_to``   (YYYY-MM-DD) — upper bound for visit_date
        - ``purpose``   — a value from Visit.VisitPurpose
        - ``farm``      — primary key of a farm owned by the agent
        - ``priority``  — a value from Visit.PriorityLevel

    Returns
    -------
    HttpResponse
        Rendered visit list page.
    """

    # django_packages
    from django.core.paginator import Paginator

    agent = request.user.agent_profile

    visits = (
        Visit.objects.filter(agent=agent)
        .select_related("farm__lga", "farm__farmer__user")
        .order_by("-visit_date", "-visit_time")
    )

    # --- Filters ---
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()
    purpose = request.GET.get("purpose", "").strip()
    farm_pk = request.GET.get("farm", "").strip()
    priority = request.GET.get("priority", "").strip()

    if date_from:
        try:
            # django_packages
            from django.utils.dateparse import parse_date

            parsed = parse_date(date_from)
            if parsed:
                visits = visits.filter(visit_date__gte=parsed)
        except ValueError:
            pass

    if date_to:
        try:
            # django_packages
            from django.utils.dateparse import parse_date

            parsed = parse_date(date_to)
            if parsed:
                visits = visits.filter(visit_date__lte=parsed)
        except ValueError:
            pass

    if purpose and purpose in Visit.VisitPurpose.values:
        visits = visits.filter(purpose=purpose)

    if farm_pk:
        try:
            visits = visits.filter(farm_id=int(farm_pk))
        except (ValueError, TypeError):
            pass

    if priority and priority in Visit.PriorityLevel.values:
        visits = visits.filter(priority_level=priority)

    # Farm filter dropdown is scoped to the agent's own visits' farms
    # so the agent cannot filter by a farm they have never visited.
    agent_farm_ids = (
        Visit.objects.filter(agent=agent).values_list("farm_id", flat=True).distinct()
    )
    filter_farms = (
        Farm.objects.filter(id__in=agent_farm_ids)
        .select_related("lga")
        .order_by("name")
    )

    paginator = Paginator(visits, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "filter_farms": filter_farms,
        "purpose_choices": Visit.VisitPurpose.choices,
        "priority_choices": Visit.PriorityLevel.choices,
        # Preserve active filter values so the template can
        # re-populate the filter panel after a GET submission.
        "active_filters": {
            "date_from": date_from,
            "date_to": date_to,
            "purpose": purpose,
            "farm": farm_pk,
            "priority": priority,
        },
    }

    return render(
        request=request,
        template_name="visits/pages/visit_list_page.html",
        context=context,
    )
