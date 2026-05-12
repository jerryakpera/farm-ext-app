"""
Views for the farms app.
"""

# django_packages
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

# other_apps_packages
from core.profiles.decorators import agent_required

# app_packages
from .forms import FarmDetailsForm, FarmImageUploadForm, FarmVerificationForm
from .models import Farm


def get_farmer_farm_or_404(request, farm_id):
    """
    Return a farm only if it belongs to the requesting farmer,
    preventing unauthorized access to other farmers' farms.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request containing the authenticated user.
    farm_id : int
        The primary key of the farm to retrieve.

    Returns
    -------
    Farm
        The farm object if found and owned by the requesting farmer.

    Raises
    ------
    Http404
        If the farm does not exist or does not belong to the farmer.
    """

    return get_object_or_404(Farm, pk=farm_id, farmer=request.user.farmer_profile)


@login_required
def all_farms_list_view(request):
    """
    Display all farms registered on the platform.

    Accessible to extension agents. Farmers are redirected to their
    own farm list since they should only manage their own farms.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.

    Returns
    -------
    HttpResponse
        Rendered all-farms list page.
    """
    if request.user.is_farmer:
        return redirect("farms:farm_list")

    farms = Farm.objects.select_related(
        "farmer__user", "lga", "primary_crop"
    ).prefetch_related(
        "other_crops",
        "animals",
    )

    return render(
        request=request,
        template_name="farms/pages/all_farms_list.html",
        context={"farms": farms},
    )


@login_required
def farm_list_view(request):
    """
    Display all farms that belong to the authenticated farmer.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.

    Returns
    -------
    HttpResponse
        Rendered farm list page for the authenticated farmer.
    """

    farms = (
        Farm.objects.filter(
            farmer=request.user.farmer_profile,
        )
        .select_related("lga", "primary_crop")
        .prefetch_related(
            "other_crops",
            "animals",
        )
    )

    context = {
        "farms": farms,
    }

    return render(
        request=request,
        template_name="farms/pages/farm_list.html",
        context=context,
    )


@login_required
def farm_create_view(request):
    """
    Handle creation of a new farm for the authenticated farmer.

    GET displays an empty form.
    POST validates input and creates a new farm.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.

    Returns
    -------
    HttpResponse
        Rendered farm creation page or redirect to the created farm detail page.
    """

    if request.method == "POST":
        form = FarmDetailsForm(request.POST)
        if form.is_valid():
            farm = form.save(farmer=request.user.farmer_profile)
            messages.success(request, "Farm created successfully.")

            return redirect("farms:farm_detail", farm_id=farm.pk)
    else:
        form = FarmDetailsForm()

    context = {
        "form": form,
    }

    return render(
        request=request,
        context=context,
        template_name="farms/pages/create_farm_page.html",
    )


@login_required
def farm_detail_view(request, farm_id):
    """
    Display details of a single farm.

    Farmers may only view their own farms — ownership is enforced via
    get_farmer_farm_or_404. Extension agents may view any farm on the
    platform without an ownership check.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    farm_id : int
        The primary key of the farm to retrieve.

    Returns
    -------
    HttpResponse
        Rendered farm detail page.
    """

    if request.user.is_farmer:
        farm_exists = Farm.objects.filter(
            pk=farm_id,
            farmer=request.user.farmer_profile,
        ).exists()

        if farm_exists:
            farm = get_farmer_farm_or_404(request, farm_id)
        else:
            messages.error(
                request=request,
                message="You are not authorized to view this farm.",
            )

            return redirect("farms:farm_list")

    else:
        farm = get_object_or_404(
            Farm.objects.select_related(
                "lga",
                "farmer__user",
                "primary_crop",
            ).prefetch_related(
                "animals",
                "other_crops",
            ),
            pk=farm_id,
        )

    context = {
        "farm": farm,
        "image_form": FarmImageUploadForm() if request.user.is_farmer else None,
    }

    return render(
        request=request,
        context=context,
        template_name="farms/pages/farm_detail.html",
    )


@login_required
def farm_edit_view(request, farm_id):
    """
    Handle updating an existing farm.

    GET displays the pre-filled form.
    POST validates and saves updates.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    farm_id : int
        The primary key of the farm to edit.

    Returns
    -------
    HttpResponse
        Rendered edit form or redirect to the farm detail page.
    """

    farm = get_farmer_farm_or_404(request, farm_id)

    if request.method == "POST":
        form = FarmDetailsForm(request.POST, farm=farm)
        if form.is_valid():
            form.save(farmer=request.user.farmer_profile, farm=farm)
            messages.success(request, "Farm updated successfully.")
            return redirect("farms:farm_detail", farm_id=farm.pk)
    else:
        form = FarmDetailsForm(farm=farm)

    context = {
        "form": form,
        "farm": farm,
    }

    return render(
        request=request,
        context=context,
        template_name="farms/pages/edit_farm_page.html",
    )


@login_required
def farm_delete_view(request, farm_id):
    """
    Handle deletion of a farm.

    GET displays a confirmation page.
    POST deletes the farm and redirects to the farm list.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    farm_id : int
        The primary key of the farm to delete.

    Returns
    -------
    HttpResponse
        Rendered confirmation page or redirect to farm list.
    """

    farm = get_farmer_farm_or_404(request, farm_id)

    if request.method == "POST":
        name = farm.name
        farm.delete()
        messages.success(request, f'"{name}" has been deleted.')
        return redirect("farms:farm_list")

    return render(request, "farms/farm_confirm_delete.html", {"farm": farm})


@login_required
def farm_image_upload_view(request, farm_id):
    """
    Handle POST request to upload and update a farm's image.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request containing form data and uploaded files.
    farm_id : int
        The ID of the farm whose image is being updated.

    Returns
    -------
    HttpResponseRedirect
        Redirect to the farm detail page after processing the upload.
    """

    farm = get_farmer_farm_or_404(request, farm_id)

    if request.method == "POST":
        form = FarmImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            farm.image = form.cleaned_data["image"]
            farm.save(update_fields=["image"])
            messages.success(request, "Farm image updated successfully.")
        else:
            messages.error(request, "Upload failed. Please select a valid image file.")

    return redirect("farms:farm_detail", farm_id=farm.pk)


@agent_required
def farm_verify_view(request, farm_id):
    """
    Allow an extension agent to verify a farm after a physical visit.

    The form is pre-populated with the farmer's submitted values so the
    agent only needs to correct fields that do not match what they
    observed on site. Submitting the form overwrites the farm record
    with the agent's values and marks the farm as verified.

    GET displays the pre-filled verification form alongside read-only
    farm metadata.
    POST validates the form, saves the corrected values, marks the farm
    as verified, and redirects to the farm detail page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    farm_id : int
        The primary key of the farm to verify.

    Returns
    -------
    HttpResponse
        Rendered verification form or redirect after successful verification.
    """

    farm = get_object_or_404(
        Farm.objects.select_related(
            "farmer__user", "lga", "ward", "primary_crop", "verified_by__user"
        ).prefetch_related("other_crops", "animals"),
        pk=farm_id,
    )

    if farm.is_verified:
        messages.info(request, f'"{farm.name}" has already been verified.')
        return redirect("farms:farm_detail", farm_id=farm.pk)

    if request.method == "POST":
        form = FarmVerificationForm(request.POST, request.FILES, farm=farm)
        if form.is_valid():
            form.save(farm=farm, agent=request.user.agent_profile)
            messages.success(
                request,
                f'"{farm.name}" has been verified successfully.',
            )
            return redirect("farms:farm_detail", farm_id=farm.pk)
    else:
        form = FarmVerificationForm(farm=farm)

    return render(
        request,
        "farms/pages/verify_farm.html",
        {
            "form": form,
            "farm": farm,
        },
    )
