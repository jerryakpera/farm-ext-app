"""
Models for the farms app.
"""

# django_packages
from django.db import models

# other_apps_packages
from core.common.models import LGA
from core.profiles.models import ExtensionAgentProfile, FarmerProfile


class Crop(models.Model):
    """
    A reference crop that can be associated with one or more farms.
    """

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Crop"
        verbose_name_plural = "Crops"
        ordering = ["name"]

    def __str__(self):
        """
        Return the string representation of the crop.

        Returns
        -------
        str
            The crop name.
        """

        return self.name


class Farm(models.Model):
    """
    Represents a farm registered by a farmer.
    """

    farmer = models.ForeignKey(
        FarmerProfile,
        on_delete=models.CASCADE,
        related_name="farms",
    )
    lga = models.ForeignKey(
        LGA,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="farms",
    )
    name = models.CharField(max_length=255)
    address = models.TextField(
        blank=True,
        help_text="Street address or nearest landmark.",
    )
    image = models.ImageField(
        upload_to="farm_images/",
        null=True,
        blank=True,
        help_text="A single representative image of the farm.",
    )
    size = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Farm size in hectares.",
    )
    primary_crop = models.ForeignKey(
        Crop,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_farms",
        help_text="The main crop grown on this farm.",
    )
    other_crops = models.ManyToManyField(
        Crop,
        blank=True,
        related_name="secondary_farms",
        help_text="Additional crops grown on this farm.",
    )

    is_verified = models.BooleanField(
        default=False,
        help_text="Set to True by an extension agent after physical verification.",
    )
    verified_by = models.ForeignKey(
        ExtensionAgentProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_farms",
        help_text="The extension agent who verified this farm.",
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of when the farm was verified.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Farm"
        verbose_name_plural = "Farms"
        ordering = ["-created_at"]

    def __str__(self):
        """
        Return the string representation of the farm.

        Returns
        -------
        str
            The farm name and the farmer's full name.
        """

        return f"{self.name} — {self.farmer.user.full_name}"
