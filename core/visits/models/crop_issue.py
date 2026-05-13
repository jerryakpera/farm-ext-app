"""
Models for the visits app.
"""

# django_packages
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# app_packages
from .choices import Severity
from .visit import Visit
from .visit_crop_analysis import VisitCropAnalysis


class CropIssue(models.Model):
    """
    Represents a specific issue or abnormal condition identified during a crop analysis.
    """

    class IssueType(models.TextChoices):
        """
        Types of crop-related problems observed during field visits.
        """

        POOR_GERMINATION = "poor_germination", "Poor Germination"
        YELLOW_LEAVES = "yellow_leaves", "Yellow Leaves"
        STUNTED_GROWTH = "stunted_growth", "Stunted Growth"
        PEST_ATTACK = "pest_attack", "Pest Attack"
        DISEASE_INFECTION = "disease_infection", "Disease Infection"
        DROUGHT_STRESS = "drought_stress", "Drought Stress"
        WATERLOGGING = "waterlogging", "Waterlogging"
        FERTILIZER_MISAPPLICATION = (
            "fertilizer_misapplication",
            "Fertilizer Misapplication",
        )
        LOW_POPULATION = "low_plant_population", "Low Plant Population"

    analysis = models.ForeignKey(
        "VisitCropAnalysis",
        on_delete=models.CASCADE,
        related_name="issues",
    )

    issue_type = models.CharField(max_length=50, choices=IssueType.choices)

    notes = models.TextField(blank=True)

    def __str__(self):
        """
        Return a human-readable representation of the crop issue.

        Returns
        -------
        str
            The issue type combined with the related crop analysis reference.
        """
        return f"{self.get_issue_type_display()} — {self.analysis}"


class CropAction(models.Model):
    """
    Recommended actions or interventions for issues identified during a crop analysis.
    """

    class ActionType(models.TextChoices):
        """
        Supported advisory actions for crop-related issues.
        """

        APPLY_FERTILIZER = "apply_fertilizer", "Apply Fertilizer"
        SPRAY_PESTICIDE = "spray_pesticide", "Spray Pesticide"
        WEED_IMMEDIATELY = "weed_immediately", "Weed Immediately"
        IRRIGATE = "irrigate", "Irrigate"
        REPLANT = "replant", "Replant Missing Stands"
        IMPROVE_DRAINAGE = "improve_drainage", "Improve Drainage"
        CONTACT_SPECIALIST = "contact_specialist", "Contact Specialist"
        MONITOR = "monitor", "Monitor for One Week"

    analysis = models.ForeignKey(
        "VisitCropAnalysis",
        on_delete=models.CASCADE,
        related_name="actions",
    )

    action_type = models.CharField(max_length=50, choices=ActionType.choices)

    notes = models.TextField(
        blank=True,
        help_text="Additional detail for this action.",
    )

    def __str__(self):
        """
        Return a human-readable representation of the crop action.

        Returns
        -------
        str
            The action type combined with the related crop analysis reference.
        """
        return f"{self.get_action_type_display()} — {self.analysis}"


class PestIncidence(models.Model):
    """
    Records a pest occurrence identified during a crop analysis visit.
    """

    analysis = models.ForeignKey(
        VisitCropAnalysis,
        on_delete=models.CASCADE,
        related_name="pest_incidences",
    )
    pest = models.CharField(max_length=100)
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
        default=Severity.LOW,
    )

    def __str__(self):
        """
        Return a human-readable representation of the pest incidence.

        Returns
        -------
        str
            The pest name and severity level associated with the crop analysis.
        """
        return f"{self.pest} ({self.get_severity_display()}) — {self.analysis}"


class VisitFarmerFeedback(models.Model):
    """
    Model to track the farmer feedback from a visit.
    """

    visit = models.OneToOneField(
        Visit,
        on_delete=models.CASCADE,
        related_name="farmer_feedback",
    )

    advice_understood_by_farmer = models.BooleanField(
        default=True,
    )

    farmer_satisfaction_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    farmer_comments = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Return a human-readable representation of farmer feedback for a visit.

        Returns
        -------
        str
            A summary referencing the associated visit identifier.
        """
        return f"Feedback for Visit #{self.visit_id}"
