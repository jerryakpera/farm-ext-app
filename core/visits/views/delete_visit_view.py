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
from ..utils import can_edit_visit


@agent_required
def delete_visit_view(request, pk):
    """
    Handle deletion of an existing visit.

    GET displays a confirmation page naming the visit to be deleted.
    POST deletes the visit and all its child records, then redirects
    to the visit list with a success message.

    Deletion is restricted to the agent who logged the visit and
    superusers. Any other authenticated agent is redirected to the
    visit detail page with an error message.

    Child records are deleted automatically by the database via the
    CASCADE constraints defined on each child model's FK to Visit.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    pk : int
        The primary key of the visit to delete.

    Returns
    -------
    HttpResponse
        Rendered confirmation page or redirect after deletion.
    """

    visit = get_object_or_404(
        Visit.objects.select_related("agent__user", "farm"),
        pk=pk,
    )

    permitted, reason = can_edit_visit(request.user, visit)
    if not permitted:
        messages.error(request, reason)
        return redirect("visits:detail", pk=visit.pk)

    if request.method == "POST":
        farm_name = visit.farm.name
        visit_date = visit.visit_date
        visit.delete()
        messages.success(
            request,
            f"Visit to {farm_name} on {visit_date} has been deleted.",
        )
        return redirect("visits:list")

    return render(
        request=request,
        template_name="visits/pages/visit_confirm_delete.html",
        context={"visit": visit},
    )
