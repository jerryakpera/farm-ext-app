"""
Models for the visits app.
"""

# django_packages
from django.db import models

# other_apps_packages
from core.common import utils as common_utils, validators as common_validators
from core.farms.models import Farm
from core.profiles.models import ExtensionAgentProfile


class Visit(models.Model):
    """
    Represents a physical visit made by an extension agent to a registered farm.
    """

    class VisitPurpose(models.TextChoices):
        """
        Supported reasons or objectives for carrying out a farm visit.
        """

        ROUTINE_MONITORING = "routine_monitoring", "Routine Monitoring"
        PROBLEM_DIAGNOSIS = "problem_diagnosis", "Problem Diagnosis"
        ADVISORY_FOLLOW_UP = "advisory_follow_up", "Advisory Follow-up"
        PEST_DISEASE_INSPECTION = "pest_disease_inspection", "Pest/Disease Inspection"
        SOIL_ASSESSMENT = "soil_assessment", "Soil Assessment"
        FERTILIZER_RECOMMENDATION = (
            "fertilizer_recommendation",
            "Fertilizer Recommendation",
        )
        PRE_HARVEST_INSPECTION = "pre_harvest_inspection", "Pre-Harvest Inspection"
        FARM_VERIFICATION = "farm_verification", "Farm Verification"
        YIELD_ASSESSMENT = "yield_assessment", "Yield Assessment"
        OTHER = "other", "Other"

    class PriorityLevel(models.TextChoices):
        """
        Priority levels used to indicate the urgency of follow-up actions.
        """

        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class VisitOutcome(models.TextChoices):
        """
        Possible outcomes or resolutions resulting from a farm visit.
        """

        ADVICE_PROVIDED = "advice_provided", "Advice Provided Successfully"
        ESCALATED = "escalated", "Escalated to Specialist"
        VERIFIED = "verified", "Verification Completed"
        FOLLOW_UP = "follow_up", "Follow-up Scheduled"

    agent = models.ForeignKey(
        ExtensionAgentProfile,
        on_delete=models.CASCADE,
        related_name="visits",
        help_text="The extension agent who carried out the visit.",
    )

    farm = models.ForeignKey(
        Farm,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="visits",
        help_text="The farm which was visited",
    )

    visit_date = models.DateField(
        help_text="The calendar date when the visit took place.",
    )
    visit_time = models.TimeField(
        null=True,
        blank=True,
        help_text="The exact time the visit started, if available.",
    )

    purpose = models.CharField(
        max_length=255,
        choices=VisitPurpose.choices,
        default=VisitPurpose.ROUTINE_MONITORING,
        help_text="The main reason for carrying out the visit.",
    )

    purpose_other = models.CharField(
        max_length=255,
        blank=True,
        help_text="Additional details when the purpose is marked as 'Other'.",
    )

    farm_photo = models.ImageField(
        null=True,
        blank=True,
        upload_to=common_utils.file_upload_path,
        validators=[
            common_validators.validate_image_size,
            common_validators.validate_image_format,
        ],
        help_text="A photo taken of the farm during the visit.",
    )

    pest_photo = models.ImageField(
        null=True,
        blank=True,
        upload_to=common_utils.file_upload_path,
        validators=[
            common_validators.validate_image_size,
            common_validators.validate_image_format,
        ],
        help_text="A photo showing any pests or disease signs observed.",
    )

    soil_photo = models.ImageField(
        null=True,
        blank=True,
        upload_to=common_utils.file_upload_path,
        validators=[
            common_validators.validate_image_size,
            common_validators.validate_image_format,
        ],
        help_text="A photo of the soil condition taken during the visit.",
    )

    attachment = models.FileField(
        null=True,
        blank=True,
        upload_to=common_utils.file_upload_path,
        help_text="Any supporting documents or files related to the visit.",
    )

    follow_up_required = models.BooleanField(
        default=False,
        help_text="Indicates whether another visit is needed.",
    )
    follow_up_date = models.DateField(
        null=True,
        blank=True,
        help_text="The scheduled date for the follow-up visit, if required.",
    )

    priority_level = models.CharField(
        max_length=10,
        choices=PriorityLevel.choices,
        default=PriorityLevel.LOW,
        help_text="Indicates how urgent the follow-up or issue is.",
    )

    outcome = models.CharField(
        max_length=30,
        choices=VisitOutcome.choices,
        blank=True,
        help_text="The final result or status of the visit.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time when this visit record was created.",
    )

    class Meta:
        ordering = ["-visit_date", "-visit_time"]

    def __str__(self):
        return f"Visit to {self.farm.name} by {self.agent.user.full_name} on {self.visit_date}"
