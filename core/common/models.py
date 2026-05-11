"""
Models for the common app.
"""

# django_packages
from django.db import models


# Create your models here.
class LGA(models.Model):
    """
    Local Government Area reference table.
    """

    name = models.CharField(max_length=100, unique=True)
    state = models.CharField(max_length=100, default="Plateau")

    class Meta:
        verbose_name = "LGA"
        verbose_name_plural = "LGAs"
        ordering = ["name"]

    def __str__(self):
        """
        Return the string representation of the LGA.

        Returns
        -------
        str
            The LGA name and state.
        """

        return f"{self.name}, {self.state}"


class Ward(models.Model):
    """
    An administrative ward that belongs to an LGA.
    """

    lga = models.ForeignKey(
        LGA,
        on_delete=models.CASCADE,
        related_name="wards",
    )
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Ward"
        verbose_name_plural = "Wards"
        ordering = ["name"]

    def __str__(self) -> str:
        """
        Return the string representation of the Ward.

        Returns
        -------
        str
            The Ward name and LGA name.
        """

        return f"{self.name} ({self.lga.name})"
