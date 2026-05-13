"""
Admin registration for the visits app.
"""

# django_packages
from django.contrib import admin

# app_packages
from .models import (
    CropAction,
    CropIssue,
    LivestockAction,
    LivestockDiseaseIncidence,
    LivestockIssue,
    PestIncidence,
    Visit,
    VisitCropAnalysis,
    VisitFarmerFeedback,
    VisitIssue,
    VisitLivestockAnalysis,
)


# ---------------------------------------------------------------------------
# Visit inlines
# ---------------------------------------------------------------------------


class VisitIssueInline(admin.TabularInline):
    """
    Inline admin interface for managing issues recorded during a visit.
    """

    model = VisitIssue
    extra = 0
    fields = ("title", "severity", "description")


class VisitFarmerFeedbackInline(admin.StackedInline):
    """
    Inline admin interface for capturing farmer feedback related to a visit.
    """

    model = VisitFarmerFeedback
    extra = 0
    fields = (
        "advice_understood_by_farmer",
        "farmer_satisfaction_rating",
        "farmer_comments",
    )


# ---------------------------------------------------------------------------
# CropAnalysis inlines
# ---------------------------------------------------------------------------


class CropIssueInline(admin.TabularInline):
    """
    Inline admin interface for managing crop issues identified during a visit analysis.
    """

    model = CropIssue
    extra = 0
    fields = ("issue_type", "notes")


class CropActionInline(admin.TabularInline):
    """
    Inline admin interface for managing recommended crop actions during a visit analysis.
    """

    model = CropAction
    extra = 0
    fields = ("action_type", "notes")


class PestIncidenceInline(admin.TabularInline):
    """
    Inline admin interface for recording pest occurrences during crop analysis.
    """

    model = PestIncidence
    extra = 0
    fields = ("pest", "severity")


# ---------------------------------------------------------------------------
# LivestockAnalysis inlines
# ---------------------------------------------------------------------------


class LivestockIssueInline(admin.TabularInline):
    """
    Inline admin interface for managing livestock issues identified during analysis.
    """

    model = LivestockIssue
    extra = 0
    fields = ("issue_type", "notes")


class LivestockActionInline(admin.TabularInline):
    """
    Inline admin interface for managing livestock-related recommended actions.
    """

    model = LivestockAction
    extra = 0
    fields = ("action_type", "notes")


class LivestockDiseaseIncidenceInline(admin.TabularInline):
    """
    Inline admin interface for recording livestock disease incidences during visits.
    """

    model = LivestockDiseaseIncidence
    extra = 0
    fields = ("disease_name", "severity", "confidence_level", "animals_affected_count")


# ---------------------------------------------------------------------------
# ModelAdmin registrations
# ---------------------------------------------------------------------------


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    """
    Admin interface for managing farm visits conducted by extension agents.
    """

    list_display = (
        "id",
        "agent",
        "visit_date",
        "purpose",
        "priority_level",
        "outcome",
        "follow_up_required",
    )
    list_filter = (
        "purpose",
        "priority_level",
        "outcome",
        "follow_up_required",
        "visit_date",
    )
    search_fields = (
        "farm__name",
        "agent__user__first_name",
        "agent__user__last_name",
        "agent__user__email",
    )
    date_hierarchy = "visit_date"
    inlines = [
        VisitIssueInline,
        VisitFarmerFeedbackInline,
    ]


@admin.register(VisitCropAnalysis)
class VisitCropAnalysisAdmin(admin.ModelAdmin):
    """
    Admin interface for managing crop analysis records linked to farm visits.
    """

    list_display = (
        "id",
        "visit",
        "crop",
        "variety",
        "crop_stage",
        "crop_condition",
        "weed_presence",
    )
    list_filter = (
        "crop_stage",
        "crop_condition",
        "weed_presence",
    )
    search_fields = (
        "crop__name",
        "visit__farm__name",
        "variety__name",
    )
    inlines = [
        CropIssueInline,
        CropActionInline,
        PestIncidenceInline,
    ]


@admin.register(VisitLivestockAnalysis)
class VisitLivestockAnalysisAdmin(admin.ModelAdmin):
    """
    Admin interface for managing livestock analysis records linked to farm visits.
    """

    list_display = (
        "id",
        "visit",
        "animal",
        "production_purpose",
        "overall_condition",
        "total_population",
        "number_sick",
        "ectoparasite_presence",
    )
    list_filter = (
        "production_purpose",
        "housing_system",
        "overall_condition",
        "ectoparasite_presence",
    )
    search_fields = (
        "animal__name",
        "visit__farm__name",
        "breed_or_variety",
    )
    inlines = [
        LivestockIssueInline,
        LivestockActionInline,
        LivestockDiseaseIncidenceInline,
    ]
