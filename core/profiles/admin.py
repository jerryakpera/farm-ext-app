"""
Admin config for the profiles app.
"""

# django_packages
from django.contrib import admin

# app_packages
from .models import ExtensionAgentProfile, ExtensionAgentWhitelist, FarmerProfile


@admin.register(ExtensionAgentWhitelist)
class ExtensionAgentWhitelistAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing extension agent whitelist entries.
    """

    list_display = ("email", "added_by", "date_added", "is_used")
    list_filter = ("is_used",)
    search_fields = ("email",)
    readonly_fields = ("date_added", "is_used")


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing farmer profiles.
    """

    list_display = ("user", "lga", "date_of_birth")
    search_fields = ("user__full_name", "user__email")
    list_filter = ("lga",)


@admin.register(ExtensionAgentProfile)
class ExtensionAgentProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing extension agent profiles.
    """

    list_display = ("user", "staff_id", "agency_name")
    search_fields = ("user__full_name", "user__email", "staff_id")
    filter_horizontal = ("assigned_lgas",)
