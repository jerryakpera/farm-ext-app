"""
Models for the visits app — disease incidences observed in livestock during a visit.
"""

# django_packages
from django.db import models

# app_packages
from .choices import Severity
from .visit_livestock_analysis import VisitLivestockAnalysis


class LivestockDiseaseIncidence(models.Model):
    """
    Records a specific disease or suspected condition observed in a
    livestock species during a farm visit.

    Multiple disease incidences can be linked to the same analysis,
    since a herd may present more than one condition simultaneously.
    """

    class ConfidenceLevel(models.TextChoices):
        """
        How confident the agent is in the diagnosis.
        """

        SUSPECTED = "suspected", "Suspected"
        PROBABLE = "probable", "Probable"
        CONFIRMED = "confirmed", "Confirmed (Lab or Vet)"

    analysis = models.ForeignKey(
        VisitLivestockAnalysis,
        on_delete=models.CASCADE,
        related_name="disease_incidences",
        help_text="The livestock analysis this disease incidence belongs to.",
    )
    disease_name = models.CharField(
        max_length=150,
        help_text="Name of the disease or condition observed or suspected.",
    )
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
        default=Severity.LOW,
        help_text="How severe this disease incidence is.",
    )
    confidence_level = models.CharField(
        max_length=15,
        choices=ConfidenceLevel.choices,
        default=ConfidenceLevel.SUSPECTED,
        help_text="How certain the agent is about this diagnosis.",
    )
    symptoms_observed = models.TextField(
        blank=True,
        help_text="Clinical signs or symptoms noted in the affected animals.",
    )
    animals_affected_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated number of animals showing signs of this condition.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Livestock Disease Incidence"
        verbose_name_plural = "Livestock Disease Incidences"
        ordering = ["-severity"]

    def __str__(self):
        """
        Return the string representation of the disease incidence.

        Returns
        -------
        str
            The disease name, severity, and the analysis it belongs to.
        """

        return (
            f"{self.disease_name} ({self.get_severity_display()}) " f"— {self.analysis}"
        )
