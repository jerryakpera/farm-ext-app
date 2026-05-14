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
    VisitFarmerFeedbackForm,
    VisitFollowUpForm,
    VisitIssueForm,
    VisitMediaForm,
)
from ..models import Visit, VisitFarmerFeedback


@agent_required
def add_visit_issue_view(request, visit_pk):
    """
    Handle addition of a single general issue to an existing visit.

    The visit FK is fetched from the URL and attached to the VisitIssue
    instance before saving.

    Access is restricted to the agent who logged the visit.

    GET displays an empty VisitIssueForm.
    POST validates the form, attaches the visit FK, saves the record,
    and redirects back to the visit detail page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    visit_pk : int
        The primary key of the visit this issue belongs to.

    Returns
    -------
    HttpResponse
        Rendered form page or redirect to the visit detail page.
    """

    visit = get_object_or_404(
        Visit.objects.select_related("agent"),
        pk=visit_pk,
    )

    if visit.agent != request.user.agent_profile and not request.user.is_superuser:
        messages.error(request, "You are not authorised to add issues to this visit.")

        return redirect("visits:detail", pk=visit.pk)

    if request.method == "POST":
        form = VisitIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.visit = visit
            issue.save()

            messages.success(request, "Issue added successfully.")

            return redirect("visits:detail", pk=visit.pk)
    else:
        form = VisitIssueForm()

    return render(
        request=request,
        template_name="visits/form_page.html",
        context={
            "form": form,
            "visit": visit,
            "heading": "Add Visit Issue",
            "cancel_url": reverse("visits:detail", kwargs={"pk": visit.pk}),
            "submit_label": "Save Issue",
        },
    )


@agent_required
def add_visit_media_view(request, pk):
    """
    Handle upload of photos and attachments for an existing visit.

    VisitMediaForm is a ModelForm on Visit itself, so the existing visit
    instance is passed directly via ``instance=``. This means a valid
    POST updates the Visit record in place rather than creating a new one.

    Access is restricted to the agent who logged the visit.

    GET displays VisitMediaForm pre-populated with any media already
    saved on the visit.
    POST validates the form and saves the uploaded files to the visit,
    then redirects back to the visit detail page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    pk : int
        The primary key of the visit to attach media to.

    Returns
    -------
    HttpResponse
        Rendered form page or redirect to the visit detail page.
    """

    visit = get_object_or_404(
        Visit.objects.select_related("agent"),
        pk=pk,
    )

    if visit.agent != request.user.agent_profile and not request.user.is_superuser:
        messages.error(request, "You are not authorised to add media to this visit.")
        return redirect("visits:detail", pk=visit.pk)

    if request.method == "POST":
        form = VisitMediaForm(request.POST, request.FILES, instance=visit)
        if form.is_valid():
            form.save()
            messages.success(request, "Media uploaded successfully.")
            return redirect("visits:detail", pk=visit.pk)
    else:
        form = VisitMediaForm(instance=visit)

    return render(
        request=request,
        template_name="visits/form_page.html",
        context={
            "form": form,
            "visit": visit,
            "heading": "Upload Media",
            "cancel_url": reverse("visits:detail", kwargs={"pk": visit.pk}),
            "submit_label": "Save Media",
        },
    )


@agent_required
def add_visit_followup_view(request, pk):
    """
    Handle recording or updating the follow-up plan for an existing visit.

    VisitFollowUpForm is a ModelForm on Visit itself, so the existing
    visit instance is passed directly via ``instance=``. A valid POST
    updates the Visit record in place.

    Access is restricted to the agent who logged the visit.

    GET displays VisitFollowUpForm pre-populated with any follow-up
    data already saved on the visit.
    POST validates the form, enforces the conditional follow_up_date
    requirement via the form's clean() method, saves the record, and
    redirects back to the visit detail page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    pk : int
        The primary key of the visit to record a follow-up plan for.

    Returns
    -------
    HttpResponse
        Rendered form page or redirect to the visit detail page.
    """

    visit = get_object_or_404(
        Visit.objects.select_related("agent"),
        pk=pk,
    )

    if visit.agent != request.user.agent_profile and not request.user.is_superuser:
        messages.error(
            request,
            "You are not authorised to update the follow-up plan for this visit.",
        )
        return redirect("visits:detail", pk=visit.pk)

    if request.method == "POST":
        form = VisitFollowUpForm(request.POST, instance=visit)
        if form.is_valid():
            form.save()
            messages.success(request, "Follow-up plan saved successfully.")
            return redirect("visits:detail", pk=visit.pk)
    else:
        form = VisitFollowUpForm(instance=visit)

    return render(
        request=request,
        template_name="visits/form_page.html",
        context={
            "form": form,
            "visit": visit,
            "heading": "Follow-up Plan",
            "cancel_url": reverse(
                "visits:detail",
                kwargs={
                    "pk": visit.pk,
                },
            ),
            "submit_label": "Save Follow-up",
        },
    )


@agent_required
def add_farmer_feedback_view(request, pk):
    """
    Handle recording or updating farmer feedback for an existing visit.

    VisitFarmerFeedback is a OneToOneField on Visit. get_or_create is
    used to fetch the existing feedback record if one exists, or
    initialise a new unsaved instance if not. The result is passed to
    VisitFarmerFeedbackForm via ``instance=`` so a valid POST either
    updates the existing record or creates it for the first time without
    risking an IntegrityError on the unique constraint.

    Access is restricted to the agent who logged the visit.

    GET displays VisitFarmerFeedbackForm pre-populated with any
    feedback already recorded for this visit.
    POST validates the form, saves the record, and redirects back to
    the visit detail page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    pk : int
        The primary key of the visit to record farmer feedback for.

    Returns
    -------
    HttpResponse
        Rendered form page or redirect to the visit detail page.
    """

    visit = get_object_or_404(
        Visit.objects.select_related("agent"),
        pk=pk,
    )

    if visit.agent != request.user.agent_profile and not request.user.is_superuser:
        messages.error(
            request,
            "You are not authorised to record feedback for this visit.",
        )
        return redirect("visits:detail", pk=visit.pk)

    feedback, _ = VisitFarmerFeedback.objects.get_or_create(visit=visit)

    if request.method == "POST":
        form = VisitFarmerFeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            form.save()
            messages.success(request, "Farmer feedback saved successfully.")
            return redirect("visits:detail", pk=visit.pk)
    else:
        form = VisitFarmerFeedbackForm(instance=feedback)

    return render(
        request=request,
        template_name="visits/form_page.html",
        context={
            "form": form,
            "visit": visit,
            "heading": "Farmer Feedback",
            "cancel_url": reverse(
                "visits:detail",
                kwargs={
                    "pk": visit.pk,
                },
            ),
            "submit_label": "Save Feedback",
        },
    )
