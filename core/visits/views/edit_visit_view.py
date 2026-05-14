"""
Views for the visits app.
"""

# django_packages
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

# other_apps_packages
from core.profiles.decorators import agent_required

# app_packages
from ..constants import VISIT_EDIT_WINDOW_HOURS
from ..forms import VisitBasicInfoForm
from ..models import Visit
from ..utils import can_edit_visit


@agent_required
def edit_visit_view(request, pk):
    """
    Handle editing of the basic information for an existing visit.

    Only the fields captured in VisitBasicInfoForm are editable here.
    All child records — crop analyses, livestock analyses, issues,
    media, follow-up, and feedback — are managed through their own
    dedicated views.

    Editing is restricted to the agent who logged the visit. Attempts
    to edit beyond VISIT_EDIT_WINDOW_HOURS hours after the visit was
    created are blocked with an error message and a redirect to the
    visit detail page.

    GET displays VisitBasicInfoForm pre-populated with the existing
    visit instance.
    POST validates the form and saves the updated record, then
    redirects to the visit detail page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    pk : int
        The primary key of the visit to edit.

    Returns
    -------
    HttpResponse
        Rendered edit page or redirect to the visit detail page.
    """

    # django_packages
    from django.utils import timezone

    visit = get_object_or_404(
        Visit.objects.select_related("agent", "farm__lga"),
        pk=pk,
    )

    permitted, reason = can_edit_visit(request.user, visit)
    if not permitted:
        messages.error(request, reason)
        return redirect("visits:detail", pk=visit.pk)

    hours_since_creation = (timezone.now() - visit.created_at).total_seconds() / 3600

    if hours_since_creation > VISIT_EDIT_WINDOW_HOURS:
        messages.error(
            request,
            f"Visits can only be edited within {VISIT_EDIT_WINDOW_HOURS} hours "
            f"of being logged. This visit can no longer be edited.",
        )
        return redirect("visits:detail", pk=visit.pk)

    agent = request.user.agent_profile

    if request.method == "POST":
        form = VisitBasicInfoForm(request.POST, instance=visit, agent=agent)
        if form.is_valid():
            form.save()
            messages.success(request, "Visit updated successfully.")
            return redirect("visits:detail", pk=visit.pk)
    else:
        form = VisitBasicInfoForm(instance=visit, agent=agent)

    return render(
        request=request,
        template_name="visits/pages/edit_visit.html",
        context={
            "form": form,
            "visit": visit,
        },
    )
