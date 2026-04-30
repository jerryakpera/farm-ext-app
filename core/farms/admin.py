"""
Admin configuration for the farms app.
"""

# django_packages
from django.contrib import admin

# app_packages
from .models import Crop, Farm


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing Crop records.
    """

    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Farm model.

    Displays key farm details with filtering by verification status and LGA.
    Farm images are managed inline on the same page.
    """

    list_display = ("name", "farmer", "primary_crop", "lga", "is_verified")
    list_filter = ("is_verified", "lga", "primary_crop")
    filter_horizontal = ("other_crops",)
