"""
Models for the visits app — livestock issues identified during a visit.
"""

# django_packages
from django.db import models

# app_packages
from .visit_livestock_analysis import VisitLivestockAnalysis


class LivestockIssue(models.Model):
    """
    A specific health or management problem identified in a livestock
    species during a farm visit.

    Multiple issues can be recorded against the same analysis.
    """

    class IssueType(models.TextChoices):
        """
        Common livestock-related issues identified during a farm visit.
        """

        DISEASE_OUTBREAK = "disease_outbreak", "Disease Outbreak"
        PARASITE_INFESTATION = "parasite_infestation", "Parasite Infestation"
        NUTRITIONAL_DEFICIENCY = "nutritional_deficiency", "Nutritional Deficiency"
        POOR_BODY_CONDITION = "poor_body_condition", "Poor Body Condition"
        REPRODUCTIVE_FAILURE = "reproductive_failure", "Reproductive Failure"
        HIGH_MORTALITY = "high_mortality", "High Mortality Rate"
        FEED_SHORTAGE = "feed_shortage", "Feed / Fodder Shortage"
        WATER_SHORTAGE = "water_shortage", "Water Shortage"
        POOR_HOUSING = "poor_housing", "Poor Housing / Shelter"
        INJURY = "injury", "Injury or Wound"
        BIOSECURITY_BREACH = "biosecurity_breach", "Biosecurity Breach"
        OTHER = "other", "Other"

    analysis = models.ForeignKey(
        VisitLivestockAnalysis,
        on_delete=models.CASCADE,
        related_name="issues",
        help_text="The livestock analysis this issue was identified in.",
    )
    issue_type = models.CharField(
        max_length=50,
        choices=IssueType.choices,
        help_text="The category of problem observed.",
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional detail about this issue.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Livestock Issue"
        verbose_name_plural = "Livestock Issues"
        ordering = ["issue_type"]

    def __str__(self):
        """
        Return the string representation of the livestock issue.

        Returns
        -------
        str
            The issue type and the analysis it belongs to.
        """

        return f"{self.get_issue_type_display()} — {self.analysis}"
