"""
Admin configuration for the common app.
"""

# django_packages
from django.contrib import admin

# app_packages
from .models import LGA


@admin.register(LGA)
class LGAAdmin(admin.ModelAdmin):
    """
    Admin configuration for the LGA model.
    """

    list_display = ("name", "state")
    search_fields = ("name",)
