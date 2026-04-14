"""
Serializers for the `verses` app.
"""

# third_party_packages
from rest_framework import serializers

# other_apps_packages
from core.verses.models import SingleVerse


class SingleVerseSerializer(serializers.ModelSerializer):
    """
    Read-only representation of a single stored verse.
    """

    class Meta:
        model = SingleVerse
        fields = ["id", "book", "chapter", "verse", "text", "version"]
        read_only_fields = fields
