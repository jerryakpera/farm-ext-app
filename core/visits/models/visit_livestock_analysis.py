"""
Models for the visits app — livestock analysis during a farm visit.
"""

# django_packages
from django.db import models

# other_apps_packages
from core.farms.models import Animal, Farm

# app_packages
from .visit import Visit


class VisitLivestockAnalysis(models.Model):
    """
    Records the condition and observations of a particular animal/livestock
    species during a farm visit.

    One visit can have multiple analyses — one per species observed.
    """

    class ProductionPurpose(models.TextChoices):
        """
        The primary reason the animal is kept on the farm.
        """

        MEAT = "meat", "Meat"
        DAIRY = "dairy", "Dairy"
        EGGS = "eggs", "Eggs"
        DRAUGHT = "draught", "Draught / Work"
        BREEDING = "breeding", "Breeding"
        MIXED = "mixed", "Mixed"
        OTHER = "other", "Other"

    class HousingSystem(models.TextChoices):
        """
        How the animals are housed or managed on the farm.
        """

        EXTENSIVE = "extensive", "Extensive (Free-Range)"
        SEMI_INTENSIVE = "semi_intensive", "Semi-Intensive"
        INTENSIVE = "intensive", "Intensive (Confined)"
        ZERO_GRAZING = "zero_grazing", "Zero Grazing"

    class OverallCondition(models.TextChoices):
        """
        The agent's overall assessment of the herd/flock condition.
        """

        EXCELLENT = "excellent", "Excellent"
        GOOD = "good", "Good"
        FAIR = "fair", "Fair"
        POOR = "poor", "Poor"

    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name="livestock_analyses",
        help_text="The visit during which this livestock analysis was recorded.",
    )
    animal = models.ForeignKey(
        Animal,
        on_delete=models.PROTECT,
        related_name="visit_analyses",
        help_text="The species of animal being assessed.",
    )

    # --- Herd / flock details ---
    breed_or_variety = models.CharField(
        max_length=100,
        blank=True,
        help_text="Breed or local variety name, if known.",
    )
    production_purpose = models.CharField(
        max_length=20,
        choices=ProductionPurpose.choices,
        blank=True,
        help_text="The primary reason this animal is kept on the farm.",
    )
    housing_system = models.CharField(
        max_length=20,
        choices=HousingSystem.choices,
        blank=True,
        help_text="How the animals are housed or managed.",
    )
    total_population = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Approximate total number of animals of this species on the farm.",
    )
    number_sick = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of animals showing signs of illness at the time of the visit.",
    )
    number_dead_this_period = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Deaths recorded since the last visit or in the current period.",
    )

    # --- Condition & welfare ---
    overall_condition = models.CharField(
        max_length=20,
        choices=OverallCondition.choices,
        blank=True,
        help_text="Agent's overall assessment of the herd or flock condition.",
    )
    body_condition_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Body condition score on a 1–5 scale, if assessed.",
    )
    feed_availability = models.CharField(
        max_length=255,
        blank=True,
        help_text="Description of the feed/fodder situation at the time of the visit.",
    )
    water_availability = models.CharField(
        max_length=255,
        blank=True,
        help_text="Description of water source availability and quality.",
    )

    # --- Health observations ---
    vaccination_status = models.CharField(
        max_length=255,
        blank=True,
        help_text="Current vaccination status or last vaccination date, if known.",
    )
    deworming_status = models.CharField(
        max_length=255,
        blank=True,
        help_text="Last deworming date or treatment history, if known.",
    )
    ectoparasite_presence = models.BooleanField(
        default=False,
        help_text="Whether ticks, lice, mites, or other ectoparasites were observed.",
    )
    general_observations = models.TextField(
        blank=True,
        help_text="General free-text observations about the livestock during this visit.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Visit Livestock Analysis"
        verbose_name_plural = "Visit Livestock Analyses"
        ordering = ["-created_at"]

    def __str__(self):
        """
        Return the string representation of the livestock analysis.

        Returns
        -------
        str
            The animal species and the visit it belongs to.
        """

        return f"{self.animal.name} analysis — Visit #{self.visit_id}"
