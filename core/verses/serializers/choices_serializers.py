"""
Serializers for the `verses` app.
"""

# third_party_packages
from rest_framework import serializers

# other_apps_packages
from core.verses.bible_structure import BIBLE_VERSE_MAP
from core.verses.choices import BibleBookChoices, BibleVersionChoices


class VerseChoicesSerializer(serializers.Serializer):
    """
    Serialize Bible version and book choices.
    """

    versions = serializers.SerializerMethodField()
    books = serializers.SerializerMethodField()
    structure = serializers.SerializerMethodField()

    def get_versions(self, obj):
        """
        Return version choices.

        Parameters
        ----------
        obj : Any
            The parent object passed by the serializer context (unused).

        Returns
        -------
        list[dict]
            List of version choices with value and label keys.
        """

        return [
            {"value": choice.value, "label": choice.label}
            for choice in BibleVersionChoices
        ]

    def get_books(self, obj):
        """
        Return book choices.

        Parameters
        ----------
        obj : Any
            The parent object passed by the serializer context (unused).

        Returns
        -------
        list[dict]
            List of book choices with value and label keys.
        """

        return [
            {"value": choice.value, "label": choice.label}
            for choice in BibleBookChoices
        ]

    def get_structure(self, obj):
        """
        Return chapter → verse mapping for all books.

        Parameters
        ----------
        obj : Any
            The parent object passed by the serializer context (unused).

        Returns
        -------
        dict
            Mapping of book identifiers to chapter-to-verse count structure.
        """

        return {
            book: {"chapters": {str(k): v for k, v in chapters.items()}}
            for book, chapters in BIBLE_VERSE_MAP.items()
        }
