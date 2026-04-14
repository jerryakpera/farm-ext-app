"""
Serializers for the `verses` app.
"""

# third_party_packages
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError

# other_apps_packages
from core.verses import validations
from core.verses.choices import BibleBookChoices, BibleVersionChoices
from core.verses.exceptions import VerseValidationError
from core.verses.models import MemoryVerse, Topic
from core.verses.services import get_or_create_memory_verse

# app_packages
from .topic_serializer import TopicSerializer


class MemoryVerseSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for MemoryVerse responses.
    """

    reference = serializers.CharField(read_only=True)
    display_text = serializers.CharField(read_only=True)

    version = serializers.SerializerMethodField()

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

    # ── Change 2: topics is now a list of topic objects ──────────────────────

    topics = TopicSerializer(many=True, read_only=True)

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
            "topics",
            "created_by",
            "created_at",
        ]
        read_only_fields = fields

    def get_version(self, obj: MemoryVerse) -> dict:
        """
        Return a structured object for the Bible version.

        Parameters
        ----------
        obj : MemoryVerse
            The instance being serialized.

        Returns
        -------
        dict
            Example::

                {
                    "value": "ENGWEBP",
                    "label": "World English Bible"
                }
        """

        raw_value = obj.verse_start.version

        try:
            label = BibleVersionChoices(raw_value).label
        except ValueError:
            label = raw_value

        return {
            "label": label,
            "value": raw_value,
        }


class MemoryVerseCreateSerializer(serializers.Serializer):
    """
    Handles creation of MemoryVerse objects.
    """

    book = serializers.ChoiceField(choices=BibleBookChoices.choices)
    chapter = serializers.IntegerField()
    verse_start = serializers.IntegerField()
    verse_end = serializers.IntegerField(required=False, allow_null=True)
    version = serializers.ChoiceField(choices=BibleVersionChoices.choices)
    topics = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.all(),
        many=True,
        required=False,
        default=list,
    )

    def validate(self, attrs):
        """
        Validate incoming MemoryVerse creation payload against all business
        rules.

        Parameters
        ----------
        attrs : dict
            Incoming validated input data containing book, chapter,
            verse_start, verse_end (optional), and version.

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

        try:
            validations.validate_memory_verse(
                book=book,
                chapter=chapter,
                verse_start=verse_start,
                verse_end=verse_end,
                version=version,
            )
        except VerseValidationError as exc:
            raise DRFValidationError({"non_field_errors": [str(exc)]})

        return attrs

    def create(self, validated_data):
        """
        Create or retrieve a MemoryVerse instance based on validated input
        data.

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

        created_by = validated_data.pop("created_by")
        topics = validated_data.pop("topics", [])

        memory_verse, _created = get_or_create_memory_verse(
            **validated_data,
            created_by=created_by,
        )

        if topics:
            memory_verse.topics.set(topics)

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

    Only ``topics`` is writable. All other fields are read-only.
    Topics are accepted as a list of Topic primary keys.
    """

    class Meta:
        model = MemoryVerse
        fields = ["topics"]
