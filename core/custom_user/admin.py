"""
Django admin configuration for the user model.
"""

# django_packages
from django.contrib import admin

# third_party_packages
from django_use_email_as_username.admin import BaseUserAdmin

# app_packages
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for managing users in the system.
    """

    list_display = ("email", "role", "is_active", "date_joined")
    list_filter = ("role", "is_active")
    search_fields = ("email", "phone_number")
    ordering = ("-date_joined",)
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "AgriConnect Fields",
            {
                "fields": ("role", "phone_number", "profile_photo"),
            },
        ),
    )
