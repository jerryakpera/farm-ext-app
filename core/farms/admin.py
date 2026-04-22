"""
Admin configuration for the farms app.
"""

# django_packages
from django.contrib import admin

# app_packages
from .models import Farm, FarmImage


class FarmImageInline(admin.TabularInline):
    """
    Inline admin for FarmImage, displayed within the Farm admin detail page.
    Allows images to be uploaded and reviewed alongside the farm record.
    """

    model = FarmImage
    extra = 1
    readonly_fields = ("uploaded_at",)


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Farm model.

    Displays key farm details with filtering by verification status and LGA.
    Farm images are managed inline on the same page.
    """

    inlines = [FarmImageInline]
    list_display = (
        "name",
        "farmer",
        "lga",
        "primary_crop",
        "size",
        "is_verified",
        "created_at",
    )
    list_filter = ("is_verified", "lga")
    search_fields = ("name", "farmer__user__full_name", "primary_crop")
    readonly_fields = ("created_at", "updated_at", "verified_at", "verified_by")
