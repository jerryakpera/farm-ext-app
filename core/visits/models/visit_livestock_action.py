"""
Models for the visits app — recommended actions for livestock during a visit.
"""

# django_packages
from django.db import models

# app_packages
from .visit_livestock_analysis import VisitLivestockAnalysis


class LivestockAction(models.Model):
    """
    A recommended intervention or action given to the farmer regarding
    their livestock during a farm visit.

    Multiple actions can be recorded against the same analysis.
    """

    class ActionType(models.TextChoices):
        """
        Recommended actions or interventions for livestock-related issues.
        """

        VACCINATE = "vaccinate", "Vaccinate Animals"
        DEWORM = "deworm", "Administer Dewormer"
        TREAT_ECTOPARASITES = "treat_ectoparasites", "Treat for Ectoparasites"
        ISOLATE_SICK = "isolate_sick", "Isolate Sick Animals"
        IMPROVE_FEED = "improve_feed", "Improve Feed / Nutrition"
        IMPROVE_WATER = "improve_water", "Improve Water Supply"
        IMPROVE_HOUSING = "improve_housing", "Improve Housing / Shelter"
        CALL_VET = "call_vet", "Call a Veterinarian"
        SUBMIT_SAMPLE = "submit_sample", "Submit Sample for Laboratory Testing"
        CULL_ANIMALS = "cull_animals", "Cull Affected Animals"
        APPLY_BIOSECURITY = "apply_biosecurity", "Apply Biosecurity Measures"
        MONITOR = "monitor", "Monitor for One Week"
        OTHER = "other", "Other"

    analysis = models.ForeignKey(
        VisitLivestockAnalysis,
        on_delete=models.CASCADE,
        related_name="actions",
        help_text="The livestock analysis this action was recommended for.",
    )
    action_type = models.CharField(
        max_length=50,
        choices=ActionType.choices,
        help_text="The type of recommended intervention.",
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional detail or instructions for carrying out this action.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Livestock Action"
        verbose_name_plural = "Livestock Actions"
        ordering = ["action_type"]

    def __str__(self):
        """
        Return the string representation of the livestock action.

        Returns
        -------
        str
            The action type and the analysis it belongs to.
        """

        return f"{self.get_action_type_display()} — {self.analysis}"
