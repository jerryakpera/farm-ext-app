"""
Views for the visits app.
"""

# django_packages
from django.contrib import messages
from django.shortcuts import redirect, render

# other_apps_packages
from core.profiles.decorators import agent_required

# app_packages
from ..forms import VisitBasicInfoForm


@agent_required
def log_visit_view(request):
    """
    Handle creation of a new visit for the authenticated extension agent.

    GET displays an empty VisitBasicInfoForm scoped to the agent's
    assigned LGAs.
    POST validates the form, attaches the agent, saves the Visit, and
    redirects to the visit detail page.

    The agent is never exposed as a form field — it is attached to the
    instance directly from the authenticated user's profile before the
    record is saved.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.

    Returns
    -------
    HttpResponse
        Rendered log-visit page or redirect to the visit detail page.
    """

    agent = request.user.agent_profile

    if request.method == "POST":
        form = VisitBasicInfoForm(request.POST, agent=agent)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.agent = agent
            visit.save()
            messages.success(request, "Visit logged successfully.")
            return redirect("visits:detail", pk=visit.pk)
    else:
        form = VisitBasicInfoForm(agent=agent)

    context = {"form": form}

    return render(
        request=request,
        context=context,
        template_name="visits/pages/log_visit_page.html",
    )
