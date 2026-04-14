"""
FilterSet for UserVerse list queries.
"""

# python_packages
from datetime import date

# third_party_packages
import django_filters

from django_filters import rest_framework as filters

# app_packages
from ..models.user_verse import LearningPhase, UserVerse


class UserVerseFilterSet(filters.FilterSet):
    """
    Supports filtering and ordering the authenticated user's verse list.

    Filters:
    phase
        Exact match against the stored phase value. Because ``phase`` is a
        computed property (not a DB column) this filter re-implements the
        tally boundary logic as Q-expression ranges so the filtering hits
        the database rather than Python.
    book
        Case-insensitive exact match on the related SingleVerse book name.
    topic
        Filter by Topic PK on the memory verse's system-wide topics.
    is_mastered
        Boolean convenience filter — True returns tally >= 128.
    ordering
        Comma-separated ordering by ``order``, ``tally``, or ``created_at``.
        Defaults to the model's natural ordering (``order`` ascending).
    """

    phase = django_filters.ChoiceFilter(
        choices=LearningPhase.choices,
        method="filter_phase",
        label="Phase",
    )
    book = django_filters.CharFilter(
        field_name="memory_verse__verse_start__book",
        lookup_expr="iexact",
        label="Book",
    )
    topic = django_filters.NumberFilter(
        field_name="memory_verse__topics",
        label="Topic ID",
    )
    is_mastered = django_filters.BooleanFilter(
        method="filter_is_mastered",
        label="Is mastered",
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("order", "order"),
            ("tally", "tally"),
            ("created_at", "created_at"),
        ),
    )

    class Meta:
        model = UserVerse
        fields = ["phase", "book", "topic", "is_mastered"]

    def filter_phase(self, queryset, name, value):
        """
        Translate the phase choice into a tally-range DB filter.

        Parameters
        ----------
        queryset : QuerySet
            The base queryset to filter.
        name : str
            The filter field name.
        value : str
            One of the LearningPhase values.

        Returns
        -------
        QuerySet
            The filtered queryset based on the selected phase.
        """

        phase_ranges = {
            LearningPhase.NOT_STARTED: {"tally": 0},
            LearningPhase.ACTIVE: {"tally__gte": 1, "tally__lte": 75},
            LearningPhase.DAILY: {"tally__gte": 76, "tally__lte": 120},
            LearningPhase.WEEKLY: {"tally__gte": 121, "tally__lte": 127},
            LearningPhase.MONTHLY: {"tally__gte": 128},
        }
        return queryset.filter(**phase_ranges.get(value, {}))

    def filter_is_mastered(self, queryset, name, value):
        """
        Filter by mastery status (tally >= 128).

        Parameters
        ----------
        queryset : QuerySet
            The base queryset to filter.
        name : str
            The filter field name.
        value : bool
            Whether to filter for mastered items.

        Returns
        -------
        QuerySet
            The filtered queryset based on mastery status.
        """

        if value:
            return queryset.filter(tally__gte=128)

        return queryset.filter(tally__lt=128)
