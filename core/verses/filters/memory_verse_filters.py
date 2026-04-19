"""
FilterSet definitions for the `verses` app.
"""

# third_party_packages
import django_filters

# other_apps_packages
from core.verses.choices import BibleBookChoices, BibleVersionChoices
from core.verses.models import MemoryVerse


class MemoryVerseFilterSet(django_filters.FilterSet):
    """
    Filters for the MemoryVerse list endpoint.
    """

    version = django_filters.ChoiceFilter(
        field_name="verse_start__version",
        choices=BibleVersionChoices.choices,
        label="Version",
    )
    book = django_filters.ChoiceFilter(
        field_name="verse_start__book",
        choices=BibleBookChoices.choices,
        label="Book",
    )
    topic = django_filters.NumberFilter(
        field_name="topics__id",
        label="Topic ID",
    )
    new = django_filters.BooleanFilter(
        method="filter_new",
        label="Exclude verses already in the requesting user's library",
    )

    class Meta:
        model = MemoryVerse
        fields = ["version", "book", "topic", "new"]

    def filter_new(self, queryset, name, value):
        """
        When ``value`` is True, exclude MemoryVerses the requesting user
        already has in their library.

        The request is available via ``self.request`` — django-filter injects
        it when the FilterSet is instantiated from a DRF view.

        Parameters
        ----------
        queryset : QuerySet[MemoryVerse]
            The base queryset being filtered.
        name : str
            The filter field name (unused — method filter receives it by
            convention).
        value : bool
            True to exclude the user's existing verses; False is a no-op.

        Returns
        -------
        QuerySet[MemoryVerse]
            Filtered queryset.
        """

        if not value:
            return queryset

        user = self.request.user

        already_added = user.user_verses.values_list("memory_verse_id", flat=True)

        return queryset.exclude(id__in=already_added)
