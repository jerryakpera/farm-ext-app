"""
Views for the visits app.
"""

# django_packages
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

# other_apps_packages
from core.profiles.decorators import agent_required

# app_packages
from ..forms import (
    LivestockActionForm,
    LivestockDiseaseIncidenceForm,
    LivestockIssueForm,
    VisitLivestockAnalysisForm,
)
from ..models import Visit, VisitLivestockAnalysis


@agent_required
def add_livestock_analysis_view(request, visit_pk):
    """
    Handle addition of a single livestock analysis to an existing visit.

    The visit FK is fetched from the URL and attached to the
    VisitLivestockAnalysis instance before saving. The form's animal
    queryset is scoped to the visit's farm by passing the visit instance
    into the form constructor.

    Access is restricted to the agent who logged the parent visit.

    GET displays an empty VisitLivestockAnalysisForm.
    POST validates the form, attaches the visit FK, saves the record,
    and redirects back to the visit detail page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    visit_pk : int
        The primary key of the visit this livestock analysis belongs to.

    Returns
    -------
    HttpResponse
        Rendered form page or redirect to the visit detail page.
    """

    visit = get_object_or_404(
        Visit.objects.select_related("farm__lga"),
        pk=visit_pk,
    )

    if visit.agent != request.user.agent_profile and not request.user.is_superuser:
        messages.error(
            request,
            "You are not authorised to add analyses to this visit.",
        )

        return redirect("visits:detail", pk=visit.pk)

    if request.method == "POST":
        form = VisitLivestockAnalysisForm(request.POST, visit=visit)
        if form.is_valid():
            analysis = form.save(commit=False)
            analysis.visit = visit
            analysis.save()
            messages.success(request, "Livestock analysis added successfully.")

            return redirect("visits:detail", pk=visit.pk)
    else:
        form = VisitLivestockAnalysisForm(visit=visit)

    return render(
        request=request,
        template_name="visits/form_page.html",
        context={
            "form": form,
            "visit": visit,
            "heading": "Add Livestock Analysis",
            "cancel_url": reverse(
                "visits:detail",
                kwargs={
                    "pk": visit.pk,
                },
            ),
            "submit_label": "Save Analysis",
        },
    )


@agent_required
def livestock_analysis_detail_view(request, visit_pk, pk):
    """
    Display a single livestock analysis and all its child records.

    Child records — issues, actions, and disease incidences — are
    prefetched in a single queryset so no additional queries are
    fired from the template.

    Access is restricted to the agent who logged the parent visit
    and superusers.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    visit_pk : int
        The primary key of the parent visit.
    pk : int
        The primary key of the livestock analysis to display.

    Returns
    -------
    HttpResponse
        Rendered livestock analysis detail page or redirect if access
        is denied.
    """

    analysis = get_object_or_404(
        VisitLivestockAnalysis.objects.select_related(
            "visit__agent__user",
            "visit__farm",
            "animal",
        ).prefetch_related(
            "issues",
            "actions",
            "disease_incidences",
        ),
        pk=pk,
        visit_id=visit_pk,
    )

    if (
        analysis.visit.agent != request.user.agent_profile
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "You are not authorised to view this livestock analysis.",
        )
        return redirect("visits:detail", pk=visit_pk)

    context = {
        "analysis": analysis,
        "visit": analysis.visit,
        "issues": analysis.issues.all(),
        "actions": analysis.actions.all(),
        "disease_incidences": analysis.disease_incidences.all(),
    }

    return render(
        request=request,
        template_name="visits/pages/livestock_analysis_detail.html",
        context=context,
    )


@agent_required
def add_livestock_issue_view(request, analysis_pk):
    """
    Handle addition of a single issue to an existing livestock analysis.

    The analysis FK is fetched from the URL and attached to the
    LivestockIssue instance before saving.

    Access is restricted to the agent who logged the parent visit.

    GET displays an empty LivestockIssueForm.
    POST validates the form, attaches the analysis FK, saves the
    record, and redirects back to the livestock analysis detail page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    analysis_pk : int
        The primary key of the livestock analysis this issue belongs to.

    Returns
    -------
    HttpResponse
        Rendered form page or redirect to the livestock analysis detail page.
    """

    analysis = get_object_or_404(
        VisitLivestockAnalysis.objects.select_related("visit__agent", "animal"),
        pk=analysis_pk,
    )

    if (
        analysis.visit.agent != request.user.agent_profile
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "You are not authorised to add issues to this analysis.",
        )
        return redirect(
            "visits:livestock_analysis_detail",
            visit_pk=analysis.visit_id,
            pk=analysis.pk,
        )

    if request.method == "POST":
        form = LivestockIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.analysis = analysis
            issue.save()

            messages.success(request, "Issue added successfully.")

            return redirect(
                "visits:livestock_analysis_detail",
                visit_pk=analysis.visit_id,
                pk=analysis.pk,
            )
    else:
        form = LivestockIssueForm()

    return render(
        request=request,
        template_name="visits/form_page.html",
        context={
            "form": form,
            "analysis": analysis,
            "heading": "Add Livestock Issue",
            "cancel_url": reverse(
                "visits:livestock_analysis_detail",
                kwargs={
                    "visit_pk": analysis.visit_id,
                    "pk": analysis.pk,
                },
            ),
            "submit_label": "Save Issue",
        },
    )


@agent_required
def add_livestock_action_view(request, analysis_pk):
    """
    Handle addition of a single recommended action to an existing
    livestock analysis.

    The analysis FK is fetched from the URL and attached to the
    LivestockAction instance before saving.

    Access is restricted to the agent who logged the parent visit.

    GET displays an empty LivestockActionForm.
    POST validates the form, attaches the analysis FK, saves the
    record, and redirects back to the livestock analysis detail page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    analysis_pk : int
        The primary key of the livestock analysis this action belongs to.

    Returns
    -------
    HttpResponse
        Rendered form page or redirect to the livestock analysis detail page.
    """

    analysis = get_object_or_404(
        VisitLivestockAnalysis.objects.select_related("visit__agent", "animal"),
        pk=analysis_pk,
    )

    if (
        analysis.visit.agent != request.user.agent_profile
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "You are not authorised to add actions to this analysis.",
        )
        return redirect(
            "visits:livestock_analysis_detail",
            visit_pk=analysis.visit_id,
            pk=analysis.pk,
        )

    if request.method == "POST":
        form = LivestockActionForm(request.POST)
        if form.is_valid():
            action = form.save(commit=False)
            action.analysis = analysis
            action.save()

            messages.success(request, "Action added successfully.")

            return redirect(
                "visits:livestock_analysis_detail",
                visit_pk=analysis.visit_id,
                pk=analysis.pk,
            )
    else:
        form = LivestockActionForm()

    return render(
        request=request,
        template_name="visits/form_page.html",
        context={
            "form": form,
            "analysis": analysis,
            "heading": "Add Recommended Action",
            "cancel_url": reverse(
                "visits:livestock_analysis_detail",
                kwargs={
                    "visit_pk": analysis.visit_id,
                    "pk": analysis.pk,
                },
            ),
            "submit_label": "Save Action",
        },
    )


@agent_required
def add_livestock_disease_view(request, analysis_pk):
    """
    Handle addition of a single disease incidence to an existing
    livestock analysis.

    The analysis FK is fetched from the URL and attached to the
    LivestockDiseaseIncidence instance before saving.

    Access is restricted to the agent who logged the parent visit.

    GET displays an empty LivestockDiseaseIncidenceForm.
    POST validates the form, attaches the analysis FK, saves the
    record, and redirects back to the livestock analysis detail page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    analysis_pk : int
        The primary key of the livestock analysis this disease incidence
        belongs to.

    Returns
    -------
    HttpResponse
        Rendered form page or redirect to the livestock analysis detail page.
    """

    analysis = get_object_or_404(
        VisitLivestockAnalysis.objects.select_related("visit__agent", "animal"),
        pk=analysis_pk,
    )

    if (
        analysis.visit.agent != request.user.agent_profile
        and not request.user.is_superuser
    ):
        messages.error(
            request,
            "You are not authorised to add disease incidences to this analysis.",
        )
        return redirect(
            "visits:livestock_analysis_detail",
            visit_pk=analysis.visit_id,
            pk=analysis.pk,
        )

    if request.method == "POST":
        form = LivestockDiseaseIncidenceForm(request.POST)
        if form.is_valid():
            incidence = form.save(commit=False)
            incidence.analysis = analysis
            incidence.save()

            messages.success(request, "Disease incidence added successfully.")

            return redirect(
                "visits:livestock_analysis_detail",
                visit_pk=analysis.visit_id,
                pk=analysis.pk,
            )
    else:
        form = LivestockDiseaseIncidenceForm()

    return render(
        request=request,
        template_name="visits/form_page.html",
        context={
            "form": form,
            "analysis": analysis,
            "heading": "Add Disease Incidence",
            "cancel_url": reverse(
                "visits:livestock_analysis_detail",
                kwargs={
                    "pk": analysis.pk,
                    "visit_pk": analysis.visit_id,
                },
            ),
            "submit_label": "Save",
        },
    )
