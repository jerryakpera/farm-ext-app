"""
Model registration for admin interface.
"""

# django_packages
from django.contrib import admin

# app_packages
from .models import DashboardWhitelist


@admin.register(DashboardWhitelist)
class DashboardWhitelistAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing dashboard whitelist entries.
    """

    list_display = ("email", "added_by", "date_added", "is_used")
    list_filter = ("is_used",)
    search_fields = ("email",)
    readonly_fields = ("date_added", "is_used")
