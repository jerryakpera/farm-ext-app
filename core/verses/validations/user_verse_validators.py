"""
Business rule validators for the verses app.

Validators are plain functions — not serializer methods — so they can be
called identically from serializers, views, and any future async tasks
without duplication.
"""

# python_packages
from datetime import date

# third_party_packages
from rest_framework.exceptions import ValidationError

# app_packages
from ..models import MemoryVerse, UserVerse


def validate_daily_verse_limit(user) -> None:
    """
    Enforce the one-new-verse-per-day business rule.

    A user may only begin learning one new verse per calendar day. This is
    determined by checking whether any of the user's verses has a
    ``learned_at`` date equal to today.

    Parameters
    ----------
    user : AUTH_USER_MODEL
        The user to check against.
    """

    already_started_today = UserVerse.objects.filter(
        user=user,
        learned_at=date.today(),
    ).exists()

    if already_started_today:
        raise ValidationError(
            "You may only begin learning one new verse per day. "
            "Come back tomorrow to start your next verse."
        )


def validate_verse_length(memory_verse: MemoryVerse) -> None:
    """
    Enforce the maximum memory verse length of 3 consecutive verses.

    A ``MemoryVerse`` is a single verse when ``verse_end`` is ``None``,
    and a range otherwise. The span is calculated inclusively from
    ``verse_start.verse`` to ``verse_end.verse``.

    Parameters
    ----------
    memory_verse : MemoryVerse
        The memory verse selection to validate.
    """

    if memory_verse.verse_end is None:
        # Single verse — always valid.
        return

    span = (memory_verse.verse_end.verse - memory_verse.verse_start.verse) + 1

    if span > 3:
        raise ValidationError(
            f"A memory verse may not exceed 3 consecutive verses. "
            f"{memory_verse.reference} spans {span}."
        )
