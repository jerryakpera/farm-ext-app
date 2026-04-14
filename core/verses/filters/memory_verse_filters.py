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

    class Meta:
        model = MemoryVerse
        fields = ["version", "book", "topic"]
