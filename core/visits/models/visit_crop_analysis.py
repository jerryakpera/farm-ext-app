"""
Models for the visits app.
"""

# django_packages
from django.db import models

# other_apps_packages
from core.farms.models import Crop, CropVariety, Farm

# app_packages
from .visit import Visit


class VisitCropAnalysis(models.Model):
    """
    Model representing the analysis of a particular crop during a farm visit.
    """

    class CropStage(models.TextChoices):
        """
        Crop growth stages.
        """

        PLANTING = "planting", "Planting"
        VEGETATIVE = "vegetative", "Vegetative"
        FLOWERING = "flowering", "Flowering"
        FRUITING = "fruiting", "Fruiting"
        HARVESTING = "harvesting", "Harvesting"

    class CropCondition(models.TextChoices):
        """
        Overall crop condition ratings.
        """

        EXCELLENT = "excellent", "Excellent"
        GOOD = "good", "Good"
        FAIR = "fair", "Fair"
        POOR = "poor", "Poor"

    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name="crop_analyses",
    )

    crop = models.ForeignKey(
        Crop,
        on_delete=models.PROTECT,
        related_name="visit_analyses",
    )

    variety = models.ForeignKey(
        CropVariety,
        null=True,
        on_delete=models.SET_NULL,
    )

    crop_stage = models.CharField(
        max_length=30,
        choices=CropStage.choices,
        blank=True,
    )

    date_planted = models.DateField(
        null=True,
        blank=True,
    )

    expected_harvest_date = models.DateField(
        null=True,
        blank=True,
    )

    crop_condition = models.CharField(
        max_length=20,
        choices=CropCondition.choices,
        blank=True,
    )

    soil_moisture_status = models.CharField(
        max_length=255,
        blank=True,
    )

    weed_presence = models.BooleanField(
        default=False,
    )

    rainfall_situation = models.TextField(
        blank=True,
    )

    observations = models.TextField(
        blank=True,
        help_text="General observations made about this crop.",
    )

    other_problem = models.TextField(
        blank=True,
    )

    recommendations = models.TextField(
        blank=True,
        help_text="Recommendations made for this crop.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Return a human-readable representation of the visit crop analysis.

        Returns
        -------
        str
            A summary combining the crop name and visit identifier.
        """

        return f"{self.crop.name} analysis — Visit #{self.visit_id}"
