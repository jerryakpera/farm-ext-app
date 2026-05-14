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
    CropActionForm,
    CropIssueForm,
    PestIncidenceForm,
    VisitCropAnalysisForm,
)
from ..models import Visit, VisitCropAnalysis


@agent_required
def add_crop_analysis_view(request, visit_pk):
    """
    Handle addition of a single crop analysis to an existing visit.

    The visit FK is fetched from the URL and attached to the
    VisitCropAnalysis instance before saving. The form's crop and
    variety querysets are scoped to the visit's farm by passing the
    visit instance into the form constructor.

    Access is restricted to the agent who logged the parent visit.

    GET displays an empty VisitCropAnalysisForm.
    POST validates the form, attaches the visit FK, saves the record,
    and redirects back to the visit detail page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    visit_pk : int
        The primary key of the visit this crop analysis belongs to.

    Returns
    -------
    HttpResponse
        Rendered form page or redirect to the visit detail page.
    """

    visit = get_object_or_404(
        Visit.objects.select_related("farm__primary_crop", "farm__lga"),
        pk=visit_pk,
    )

    if visit.agent != request.user.agent_profile and not request.user.is_superuser:
        messages.error(request, "You are not authorised to add analyses to this visit.")

        return redirect("visits:detail", pk=visit.pk)

    if request.method == "POST":
        form = VisitCropAnalysisForm(request.POST, visit=visit)
        if form.is_valid():
            analysis = form.save(commit=False)
            analysis.visit = visit
            analysis.save()

            messages.success(request, "Crop analysis added successfully.")

            return redirect("visits:detail", pk=visit.pk)
    else:
        form = VisitCropAnalysisForm(visit=visit)

    return render(
        request=request,
        template_name="visits/form_page.html",
        context={
            "form": form,
            "visit": visit,
            "heading": "Add Crop Analysis",
            "cancel_url": reverse("visits:detail", kwargs={"pk": visit.pk}),
            "submit_label": "Save Analysis",
        },
    )


@agent_required
def crop_analysis_detail_view(request, visit_pk, pk):
    """
    Display a single crop analysis and all its child records.

    Child records — issues, actions, and pest incidences — are
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
        The primary key of the crop analysis to display.

    Returns
    -------
    HttpResponse
        Rendered crop analysis detail page or redirect if access is denied.
    """

    analysis = get_object_or_404(
        VisitCropAnalysis.objects.select_related(
            "visit__agent__user",
            "visit__farm",
            "crop",
            "variety",
        ).prefetch_related(
            "issues",
            "actions",
            "pest_incidences",
        ),
        pk=pk,
        visit_id=visit_pk,
    )

    if (
        analysis.visit.agent != request.user.agent_profile
        and not request.user.is_superuser
    ):
        messages.error(request, "You are not authorised to view this crop analysis.")

        return redirect("visits:detail", pk=visit_pk)

    context = {
        "analysis": analysis,
        "visit": analysis.visit,
        "issues": analysis.issues.all(),
        "actions": analysis.actions.all(),
        "pest_incidences": analysis.pest_incidences.all(),
    }

    return render(
        request=request,
        template_name="visits/pages/crop_analysis_detail.html",
        context=context,
    )


@agent_required
def add_crop_issue_view(request, analysis_pk):
    """
    Handle addition of a single issue to an existing crop analysis.

    The analysis FK is fetched from the URL and attached to the
    CropIssue instance before saving.

    Access is restricted to the agent who logged the parent visit.

    GET displays an empty CropIssueForm.
    POST validates the form, attaches the analysis FK, saves the
    record, and redirects back to the crop analysis detail page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    analysis_pk : int
        The primary key of the crop analysis this issue belongs to.

    Returns
    -------
    HttpResponse
        Rendered form page or redirect to the crop analysis detail page.
    """

    analysis = get_object_or_404(
        VisitCropAnalysis.objects.select_related("visit__agent", "crop"),
        pk=analysis_pk,
    )

    if (
        analysis.visit.agent != request.user.agent_profile
        and not request.user.is_superuser
    ):
        messages.error(
            request, "You are not authorised to add issues to this analysis."
        )
        return redirect(
            "visits:crop_analysis_detail", visit_pk=analysis.visit_id, pk=analysis.pk
        )

    if request.method == "POST":
        form = CropIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.analysis = analysis
            issue.save()

            messages.success(request, "Issue added successfully.")

            return redirect(
                "visits:crop_analysis_detail",
                visit_pk=analysis.visit_id,
                pk=analysis.pk,
            )
    else:
        form = CropIssueForm()

    return render(
        request=request,
        template_name="visits/form_page.html",
        context={
            "form": form,
            "analysis": analysis,
            "heading": "Add Crop Issue",
            "cancel_url": reverse(
                "visits:crop_analysis_detail",
                kwargs={
                    "visit_pk": analysis.visit_id,
                    "pk": analysis.pk,
                },
            ),
            "submit_label": "Save Issue",
        },
    )


@agent_required
def add_crop_action_view(request, analysis_pk):
    """
    Handle addition of a single recommended action to an existing crop analysis.

    The analysis FK is fetched from the URL and attached to the
    CropAction instance before saving.

    Access is restricted to the agent who logged the parent visit.

    GET displays an empty CropActionForm.
    POST validates the form, attaches the analysis FK, saves the
    record, and redirects back to the crop analysis detail page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    analysis_pk : int
        The primary key of the crop analysis this action belongs to.

    Returns
    -------
    HttpResponse
        Rendered form page or redirect to the crop analysis detail page.
    """

    analysis = get_object_or_404(
        VisitCropAnalysis.objects.select_related("visit__agent", "crop"),
        pk=analysis_pk,
    )

    if (
        analysis.visit.agent != request.user.agent_profile
        and not request.user.is_superuser
    ):
        messages.error(
            request, "You are not authorised to add actions to this analysis."
        )
        return redirect(
            "visits:crop_analysis_detail",
            visit_pk=analysis.visit_id,
            pk=analysis.pk,
        )

    if request.method == "POST":
        form = CropActionForm(request.POST)
        if form.is_valid():
            action = form.save(commit=False)
            action.analysis = analysis
            action.save()

            messages.success(request, "Action added successfully.")

            return redirect(
                "visits:crop_analysis_detail",
                visit_pk=analysis.visit_id,
                pk=analysis.pk,
            )
    else:
        form = CropActionForm()

    return render(
        request=request,
        template_name="visits/form_page.html",
        context={
            "form": form,
            "analysis": analysis,
            "heading": "Add Recommended Action",
            "cancel_url": reverse(
                "visits:crop_analysis_detail",
                kwargs={
                    "visit_pk": analysis.visit_id,
                    "pk": analysis.pk,
                },
            ),
            "submit_label": "Save Action",
        },
    )


@agent_required
def add_pest_incidence_view(request, analysis_pk):
    """
    Handle addition of a single pest incidence to an existing crop analysis.

    The analysis FK is fetched from the URL and attached to the
    PestIncidence instance before saving.

    Access is restricted to the agent who logged the parent visit.

    GET displays an empty PestIncidenceForm.
    POST validates the form, attaches the analysis FK, saves the
    record, and redirects back to the crop analysis detail page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    analysis_pk : int
        The primary key of the crop analysis this pest incidence belongs to.

    Returns
    -------
    HttpResponse
        Rendered form page or redirect to the crop analysis detail page.
    """

    analysis = get_object_or_404(
        VisitCropAnalysis.objects.select_related("visit__agent", "crop"),
        pk=analysis_pk,
    )

    if (
        analysis.visit.agent != request.user.agent_profile
        and not request.user.is_superuser
    ):
        messages.error(
            request, "You are not authorised to add pest incidences to this analysis."
        )
        return redirect(
            "visits:crop_analysis_detail",
            visit_pk=analysis.visit_id,
            pk=analysis.pk,
        )

    if request.method == "POST":
        form = PestIncidenceForm(request.POST)
        if form.is_valid():
            incidence = form.save(commit=False)
            incidence.analysis = analysis
            incidence.save()
            messages.success(request, "Pest incidence added successfully.")
            return redirect(
                "visits:crop_analysis_detail",
                visit_pk=analysis.visit_id,
                pk=analysis.pk,
            )
    else:
        form = PestIncidenceForm()

    return render(
        request=request,
        template_name="visits/form_page.html",
        context={
            "form": form,
            "analysis": analysis,
            "heading": "Add Pest Incidence",
            "cancel_url": reverse(
                "visits:crop_analysis_detail",
                kwargs={
                    "visit_pk": analysis.visit_id,
                    "pk": analysis.pk,
                },
            ),
            "submit_label": "Save",
        },
    )
