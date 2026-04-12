"""
Serializer for the `SingleVerse` model.
"""

# third_party_packages
from rest_framework import serializers

# other_apps_packages
from core.verses import validations
from core.verses.choices import BibleBookChoices, BibleVersionChoices
from core.verses.models import MemoryVerse, SingleVerse
from core.verses.services import get_or_create_memory_verse


class SingleVerseSerializer(serializers.ModelSerializer):
    """
    Read-only representation of a single stored verse.
    """

    class Meta:
        model = SingleVerse
        fields = ["id", "book", "chapter", "verse", "text", "version"]
        read_only_fields = fields


class MemoryVerseSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for MemoryVerse responses.
    """

    reference = serializers.CharField(read_only=True)
    display_text = serializers.CharField(read_only=True)

    version = serializers.CharField(
        source="verse_start.version",
        read_only=True,
    )
    book = serializers.CharField(
        source="verse_start.book",
        read_only=True,
    )
    chapter = serializers.IntegerField(
        source="verse_start.chapter",
        read_only=True,
    )

    verse_start_num = serializers.IntegerField(
        source="verse_start.verse",
        read_only=True,
    )
    verse_end_num = serializers.IntegerField(
        source="verse_end.verse",
        read_only=True,
    )

    class Meta:
        model = MemoryVerse
        fields = [
            "id",
            "reference",
            "display_text",
            "version",
            "book",
            "chapter",
            "verse_start_num",
            "verse_end_num",
            "topic",
            "created_by",
            "created_at",
        ]
        read_only_fields = fields


class MemoryVerseCreateSerializer(serializers.Serializer):
    """
    Handles creation of MemoryVerse objects.
    """

    book = serializers.ChoiceField(choices=BibleBookChoices.choices)
    chapter = serializers.IntegerField()
    verse_start = serializers.IntegerField()
    verse_end = serializers.IntegerField(required=False, allow_null=True)
    version = serializers.ChoiceField(choices=BibleVersionChoices.choices)

    def validate(self, attrs):
        """
        Validate incoming MemoryVerse creation payload against all business rules.

        Parameters
        ----------
        attrs : dict
            Incoming validated input data containing book, chapter, verse_start,
            verse_end (optional), and version.

        Returns
        -------
        dict
            The validated attributes if all validation checks pass.
        """

        book = attrs["book"]
        chapter = attrs["chapter"]
        verse_start = attrs["verse_start"]
        verse_end = attrs.get("verse_end")
        version = attrs["version"]

        validations.validate_bible_version(version)
        validations.validate_bible_book(book)
        validations.validate_chapter_verse(
            book=book,
            chapter=chapter,
            verse_start=verse_start,
            verse_end=verse_end,
        )

        return attrs

    def create(self, validated_data):
        """
        Create or retrieve a MemoryVerse instance based on validated input data.

        Parameters
        ----------
        validated_data : dict
            Validated serializer data containing book, chapter, verse_start,
            verse_end (optional), and version.

        Returns
        -------
        MemoryVerse
            The created or existing MemoryVerse instance.
        """

        memory_verse, _created = get_or_create_memory_verse(**validated_data)
        return memory_verse

    def to_representation(self, instance):
        """
        Convert a MemoryVerse instance into its API representation.

        Parameters
        ----------
        instance : MemoryVerse
            The MemoryVerse model instance to serialize.

        Returns
        -------
        dict
            Serialized representation using MemoryVerseSerializer.
        """

        return MemoryVerseSerializer(instance).data


class MemoryVerseAdminSerializer(serializers.ModelSerializer):
    """
    Admin serializer for controlled updates of MemoryVerse.
    """

    class Meta:
        model = MemoryVerse
        fields = ["topic"]
