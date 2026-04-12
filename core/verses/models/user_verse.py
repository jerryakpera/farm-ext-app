"""
Models for `verses`.
"""

# django_packages
from django.conf import settings
from django.db import models

# app_packages
from .memory_verse import MemoryVerse


class LearningPhase(models.TextChoices):
    """
    The current phase of a user's learning journey for a single memory verse.
    """

    NOT_STARTED = "not_started", "Not started"
    ACTIVE = "active", "Active"
    DAILY = "daily", "Daily"
    WEEKLY = "weekly", "Weekly"
    MONTHLY = "monthly", "Monthly"


class UserVerse(models.Model):
    """
    A user's personal record of a single memory verse.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_verses",
        help_text="The user who owns this record.",
    )
    memory_verse = models.ForeignKey(
        MemoryVerse,
        on_delete=models.CASCADE,
        related_name="user_verses",
        help_text="The memory verse this record refers to.",
    )
    order = models.IntegerField(
        default=0,
        help_text=(
            "Queue position within the user's verse list. "
            "Lower values appear first. "
            "Not required to be contiguous or positive."
        ),
    )

    tally = models.PositiveIntegerField(
        default=0,
        help_text="Cumulative number of times the user has recited this verse.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "memory_verse"],
                name="unique_user_verse_per_user",
            ),
        ]
        indexes = [
            models.Index(
                fields=["user", "order"],
                name="user_verse_user_order_idx",
            ),
        ]
        ordering = ["user", "order"]
        verbose_name = "User Verse"
        verbose_name_plural = "User Verses"

    @property
    def is_not_started(self) -> bool:
        """
        Return True if the user has not yet begun learning this verse.

        Returns
        -------
        bool
            Indication if the user has begun learning this verse.
        """

        return self.tally == 0

    @property
    def phase(self) -> str:
        """
        Return the current learning phase derived from tally.

        Returns
        -------
        str
            The learning phase value derived from the tally.
        """

        if self.tally == 0:
            return LearningPhase.NOT_STARTED
        if 1 <= self.tally <= 75:
            return LearningPhase.ACTIVE
        if 76 <= self.tally <= 120:
            return LearningPhase.DAILY
        if 121 <= self.tally <= 127:
            return LearningPhase.WEEKLY
        return LearningPhase.MONTHLY

    @property
    def is_mastered(self) -> bool:
        """
        Return True if the verse has reached the monthly maintenance phase.

        Returns
        -------
        bool
            True if the verse is in the monthly phase, otherwise False.
        """

        return self.tally >= 128

    def __str__(self) -> str:
        """Return the string representation of the user verse.

        Returns
        -------
        str
            A readable string describing the user verse.
        """

        return (
            f"{self.user} — "
            f"{self.memory_verse.reference} "
            f"[{self.phase}] "
            f"tally={self.tally}"
        )
