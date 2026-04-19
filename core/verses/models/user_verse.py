"""
Models for `verses`.
"""

# python_packages
from datetime import date

# django_packages
from django.conf import settings
from django.db import models

# app_packages
from ..constants import _ACTIVE_DAY_REPS, _ACTIVE_DAY_TARGETS
from .memory_verse import MemoryVerse
from .topic import Topic


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

    topics = models.ManyToManyField(
        Topic,
        blank=True,
        related_name="user_verses",
        help_text=(
            "Optional user-defined topic overrides for this verse. "
            "When set, these replace the memory verse's system-wide topics "
            "for this user. Leave empty to inherit from the memory verse."
        ),
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

    learned_at = models.DateTimeField(
        null=True,
        help_text="When the user first began learning this verse.",
    )
    last_learned_at = models.DateTimeField(
        null=True,
        help_text="When the user last recited this verse.",
    )

    last_practiced_at = models.DateTimeField(null=True)

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

    @property
    def daily_target(self) -> int:
        """
        Return the number of recitations required today. based on the current
        phase and, within the active phase, the current day number.

        The active phase has a 5-day descending schedule derived from the
        cumulative tally, not from calendar dates, so the target is always
        unambiguous even if the user misses a day:

            Day 1 (tally 0–24)  → 25 reps
            Day 2 (tally 25–44) → 20 reps
            Day 3 (tally 45–59) → 15 reps
            Day 4 (tally 60–69) → 10 reps
            Day 5 (tally 70–74) →  5 reps

        Once a day's target is fully met the tally has crossed the boundary
        and the next day's target becomes active.

        Returns
        -------
        int
            Number of recitations required today.
            Returns 0 if the verse has not been started yet.
        """
        if self.phase == LearningPhase.NOT_STARTED:
            return 0

        if self.phase == LearningPhase.ACTIVE:
            # Find which active day the user is currently on by checking
            # which cumulative boundary has not yet been reached.
            for boundary, reps in zip(_ACTIVE_DAY_TARGETS, _ACTIVE_DAY_REPS):
                if self.tally < boundary:
                    # Reps already completed toward today's target.
                    prev_boundary = boundary - reps
                    completed_today = self.tally - prev_boundary

                    return max(reps - completed_today, 0)

            # Tally is exactly 75 — active phase complete, transition imminent.
            return 0

        if self.phase == LearningPhase.DAILY:
            return 0 if self._practiced_today else 1

        if self.phase == LearningPhase.WEEKLY:
            return 0 if self._practiced_this_week else 1

        # Monthly phase.
        return 0 if self._practiced_this_month else 1

    @property
    def _practiced_today(self) -> bool:
        """
        Return True if last_practiced_at is today.

        Returns
        -------
        bool
            True if last_practiced_at is today, otherwise False.
        """

        return bool(self.last_practiced_at and self.last_practiced_at == date.today())

    @property
    def _practiced_this_week(self) -> bool:
        """
        Return True if last_practiced_at falls in the current ISO week.

        Returns
        -------
        bool
            True if last_practiced_at is in the current ISO week, otherwise False.
        """

        if not self.last_practiced_at:
            return False

        today = date.today()

        return self.last_practiced_at.isocalendar()[:2] == today.isocalendar()[:2]

    @property
    def _practiced_this_month(self) -> bool:
        """
        Return True if last_practiced_at is in the current calendar month.

        Returns
        -------
        bool
            True if last_practiced_at is in the current month, otherwise False.
        """

        if not self.last_practiced_at:
            return False

        today = date.today()

        return (
            self.last_practiced_at.year == today.year
            and self.last_practiced_at.month == today.month
        )

    @classmethod
    def next_order_for_user(cls, user) -> int:
        """
        Return the next order value for appending a verse to the end of a
        user's queue.

        Handles an empty queryset safely by defaulting to 0.

        Parameters
        ----------
        user : AUTH_USER_MODEL
            The user whose queue is being queried.

        Returns
        -------
        int
            Return max(existing order values) + 1, or 0 if the queue is empty.
        """

        agg = cls.objects.filter(user=user).aggregate(max_order=models.Max("order"))
        current_max = agg["max_order"]

        return (current_max + 1) if current_max is not None else 0

    @classmethod
    def learn_next_order_for_user(cls, user) -> int:
        """
        Return the order value that places a verse at the front of a user's
        queue.

        Handles an empty queryset safely by defaulting to 0.

        Parameters
        ----------
        user : AUTH_USER_MODEL
            The user whose queue is being queried.

        Returns
        -------
        int
            Return min(existing order values) - 1, or 0 if the queue is empty.
        """

        agg = cls.objects.filter(user=user).aggregate(min_order=models.Min("order"))
        current_min = agg["min_order"]

        return (current_min - 1) if current_min is not None else 0

    @property
    def effective_topics(self):
        """
        Return the topics applicable to this user verse.

        The user's own topics take precedence. If the user has not set any,
        the memory verse's system-wide topics are returned instead.

        Returns
        -------
        QuerySet[Topic]
            The resolved topic queryset for this user verse.
        """

        user_topics = self.topics.all()

        if user_topics.exists():
            return user_topics

        return self.memory_verse.topics.all()

    def __str__(self) -> str:
        """
        Return the string representation of the user verse.

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
