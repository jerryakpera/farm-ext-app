"""
Admin configuration for the visits app.
"""

# django_packages
from django.contrib import admin

# app_packages
from .models import FarmVisit


@admin.register(FarmVisit)
class FarmVisitAdmin(admin.ModelAdmin):
    """
    Admin configuration for the FarmVisit model.

    Displays visit history filterable by follow-up status and visit date.
    Useful for oversight of agent activity across LGAs during the POC.
    """

    list_display = (
        "farm",
        "agent",
        "visit_date",
        "follow_up_required",
        "follow_up_date",
        "created_at",
    )
    list_filter = ("follow_up_required", "visit_date")
    search_fields = ("farm__name", "agent__user__full_name", "purpose")
    readonly_fields = ("created_at",)
