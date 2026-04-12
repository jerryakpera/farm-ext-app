"""
Models for `verses`.
"""

# django_packages
from django.db import models


class Topic(models.Model):
    """
    A thematic classification that can be applied to :class:`MemoryVerse`
    records.
    """

    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Topic"
        verbose_name_plural = "Topics"

    def __str__(self) -> str:
        """
        Returns the str representation of the model.

        Returns
        -------
        str
            Representation of the topic instance.
        """

        return self.name
