"""
Views for the farms app.
"""

# django_packages
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

# other_apps_packages
# local_packages
from core.profiles.decorators import farmer_required

# app_packages
from .forms import FarmDetailsForm, FarmImageUploadForm
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


@farmer_required
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
        .prefetch_related("other_crops")
    )

    context = {
        "farms": farms,
    }

    return render(
        request=request,
        template_name="farms/pages/farm_list.html",
        context=context,
    )


@farmer_required
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


@farmer_required
def farm_detail_view(request, farm_id):
    """
    Display details of a single farm belonging to the authenticated farmer.

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

    farm = get_farmer_farm_or_404(request, farm_id)

    return render(
        request,
        "farms/pages/farm_detail.html",
        {
            "farm": farm,
            "image_form": FarmImageUploadForm(),
        },
    )


@farmer_required
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


@farmer_required
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


@farmer_required
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
