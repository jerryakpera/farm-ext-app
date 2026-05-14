"""
Utility functions for the visits app.
"""

# django_packages
from django.utils import timezone

# app_packages
from .constants import VISIT_EDIT_WINDOW_HOURS
from .models import Visit


def get_visits_for_agent(agent_profile):
    """
    Return the base queryset of visits for a given agent with all
    commonly needed relations already fetched.

    Using this utility ensures consistent prefetching across every
    view that lists or aggregates an agent's visits, avoiding
    accidental N+1 queries when the queryset is iterated in templates.

    Parameters
    ----------
    agent_profile : ExtensionAgentProfile
        The profile of the agent whose visits are being retrieved.

    Returns
    -------
    QuerySet
        Visits belonging to the given agent, ordered by most recent
        first, with select_related and prefetch_related applied.
    """

    return (
        Visit.objects.filter(agent=agent_profile)
        .select_related(
            "agent__user",
            "farm__farmer__user",
            "farm__lga",
        )
        .prefetch_related(
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
        )
        .order_by("-visit_date", "-visit_time")
    )


def get_visits_for_farm(farm):
    """
    Return the base queryset of visits for a given farm with all
    commonly needed relations already fetched.

    Intended for use on the farm detail page and the farm visits view.
    The queryset includes all agents' visits to the farm, not just
    those of the currently authenticated user.

    Parameters
    ----------
    farm : Farm
        The farm whose visits are being retrieved.

    Returns
    -------
    QuerySet
        Visits for the given farm, ordered by most recent first,
        with select_related and prefetch_related applied.
    """

    return (
        Visit.objects.filter(farm=farm)
        .select_related(
            "agent__user",
            "farm__farmer__user",
            "farm__lga",
        )
        .prefetch_related(
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
        )
        .order_by("-visit_date", "-visit_time")
    )


def can_edit_visit(user, visit):
    """
    Determine whether a user is permitted to edit or delete a visit.

    Two conditions must both be satisfied:

    1. Ownership — the user must be the agent who logged the visit.
       Superusers bypass the ownership check.
    2. Time window — the visit must have been created within the last
       VISIT_EDIT_WINDOW_HOURS hours. The time window applies to all
       users including superusers, since edits to old visit records
       risk corrupting historical data regardless of who makes them.

    Parameters
    ----------
    user : User
        The authenticated user requesting the edit or delete.
    visit : Visit
        The visit record being edited or deleted.

    Returns
    -------
    tuple[bool, str]
        A two-tuple of (is_permitted, reason). When is_permitted is
        True, reason is an empty string. When False, reason contains
        a human-readable explanation suitable for display in a
        messages.error() call.
    """

    is_owner = user.is_superuser or visit.agent == user.agent_profile

    if not is_owner:
        return False, "You are not authorised to edit or delete this visit."

    hours_elapsed = (timezone.now() - visit.created_at).total_seconds() / 3600

    if hours_elapsed > VISIT_EDIT_WINDOW_HOURS:
        return (
            False,
            f"Visits can only be edited within {VISIT_EDIT_WINDOW_HOURS} hours "
            f"of being logged. This visit can no longer be edited.",
        )

    return True, ""


def verify_farm_from_visit(visit, agent, form):
    """
    Verify a farm atomically when a visit's purpose is FARM_VERIFICATION.

    Wraps FarmVerificationForm.save() in a database transaction so that
    the farm's verified state and the visit record are always consistent.
    If either write fails, both are rolled back.

    This function should be called from the farm verification view
    after confirming the visit purpose and form validity. It does not
    redirect or produce HTTP responses — that remains the view's
    responsibility.

    Parameters
    ----------
    visit : Visit
        The visit whose purpose is FARM_VERIFICATION. Used to confirm
        the purpose before proceeding and to associate the verification
        event with the correct visit.
    agent : ExtensionAgentProfile
        The extension agent performing the verification.
    form : FarmVerificationForm
        A valid, bound FarmVerificationForm instance. Must already have
        passed is_valid() before this function is called.

    Returns
    -------
    Farm
        The updated and verified Farm instance.

    Raises
    ------
    ValueError
        If the visit purpose is not FARM_VERIFICATION.
    """

    # django_packages
    from django.db import transaction

    if visit.purpose != Visit.VisitPurpose.FARM_VERIFICATION:
        raise ValueError(
            f"verify_farm_from_visit called on a visit with purpose "
            f"'{visit.purpose}', expected '{Visit.VisitPurpose.FARM_VERIFICATION}'."
        )

    with transaction.atomic():
        farm = form.save(farm=visit.farm, agent=agent)

    return farm
