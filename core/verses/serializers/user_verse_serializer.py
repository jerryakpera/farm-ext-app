"""
Serializers for UserVerse.
"""

# third_party_packages
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

# app_packages
from ..models import Topic
from ..models.memory_verse import MemoryVerse
from ..models.user_verse import UserVerse
from ..validations import validate_daily_verse_limit, validate_verse_length
from .memory_verse_serializer import MemoryVerseSerializer
from .topic_serializer import TopicSerializer


class UserVerseReadSerializer(serializers.ModelSerializer):
    """
    Read-only representation of a UserVerse, including all computed properties.
    """

    phase = serializers.CharField(read_only=True)
    is_mastered = serializers.BooleanField(read_only=True)
    is_not_started = serializers.BooleanField(read_only=True)
    daily_target = serializers.IntegerField(read_only=True)
    memory_verse = MemoryVerseSerializer(read_only=True)
    topics = TopicSerializer(many=True, read_only=True)
    effective_topics = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = UserVerse
        fields = [
            "id",
            "memory_verse",
            "order",
            "tally",
            "phase",
            "topics",
            "effective_topics",
            "is_mastered",
            "is_not_started",
            "daily_target",
            "learned_at",
            "last_practiced_at",
            "created_at",
        ]
        read_only_fields = fields


class UserVerseWriteSerializer(serializers.ModelSerializer):
    """
    Handles creation of a UserVerse (adding a verse to the user's backlog).

    Enforces:
    - No duplicate (user, memory_verse) pair — clean 400 instead of DB 500.
    - Memory verse must not exceed 3 consecutive verses in length.
    """

    memory_verse = serializers.PrimaryKeyRelatedField(
        queryset=MemoryVerse.objects.all(),
    )
    topics = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.all(),
        many=True,
        required=False,
        default=list,
    )

    class Meta:
        model = UserVerse
        fields = ["memory_verse", "topics"]

    def validate_memory_verse(self, memory_verse: MemoryVerse) -> MemoryVerse:
        """
        Validate that the memory verse does not exceed 3 consecutive verses.

        Parameters
        ----------
        memory_verse : MemoryVerse
            The verse instance to validate.

        Returns
        -------
        MemoryVerse
            The validated verse instance.

        Raises
        ------
        rest_framework.exceptions.ValidationError
            If the verse spans more than 3 consecutive verses.
        """

        validate_verse_length(memory_verse)

        return memory_verse

    def validate(self, attrs: dict) -> dict:
        """
        Cross-field validation: enforce daily verse limit and prevent
        duplicate (user, memory_verse).

        Parameters
        ----------
        attrs : dict
            The validated field values.

        Returns
        -------
        dict
            The validated attrs.

        Raises
        ------
        rest_framework.exceptions.ValidationError
            If the user has already started a new verse today, or if the
            verse already exists in the user's library.
        """

        user = self.context["request"].user

        validate_daily_verse_limit(user)

        if UserVerse.objects.filter(
            user=user, memory_verse=attrs["memory_verse"]
        ).exists():
            raise ValidationError(
                {"memory_verse": "This verse is already in your library."}
            )

        return attrs

    def create(self, validated_data: dict) -> UserVerse:
        """
        Create the UserVerse, assigning the requesting user and computing the
        correct queue order (append to end).

        Parameters
        ----------
        validated_data : dict
            Validated data from the serializer.

        Returns
        -------
        UserVerse
            The newly created UserVerse instance.
        """

        user = self.context["request"].user
        topics = validated_data.pop("topics", [])

        validated_data["user"] = user
        validated_data["order"] = UserVerse.next_order_for_user(user)

        instance = super().create(validated_data)

        if topics:
            instance.topics.set(topics)

        return instance


class UserVerseOrderSerializer(serializers.ModelSerializer):
    """
    Allows updating the queue `order` of a UserVerse only.
    Used for manual reordering and the 'learn next' action.
    """

    class Meta:
        model = UserVerse
        fields = ["order"]


class TallyIncrementSerializer(serializers.Serializer):
    """
    Validates an optional tally increment count.

    If `count` is omitted the view defaults to incrementing by 1.
    The count may not exceed the remaining daily target.
    """

    count = serializers.IntegerField(
        default=1,
        min_value=1,
        help_text="Number of recitations to add. Defaults to 1.",
    )

    def validate_count(self, count: int) -> int:
        """
        Ensure the increment does not exceed the remaining daily target.

        Parameters
        ----------
        count : int
            The requested increment.

        Returns
        -------
        int
            The validated count.

        Raises
        ------
        serializers.ValidationError
            If count would push the tally beyond today's target.
        """
        user_verse: UserVerse = self.context["user_verse"]
        remaining = user_verse.daily_target

        if remaining == 0:
            raise serializers.ValidationError(
                "You have already met today's target for this verse."
            )

        if count > remaining:
            raise serializers.ValidationError(
                f"Only {remaining} recitation(s) remaining to meet today's target."
            )

        return count


class UserVerseTopicsSerializer(serializers.ModelSerializer):
    """
    Allows a user to set or clear their personal topic overrides for a verse.

    Accepts a list of Topic PKs. Passing an empty list clears the override
    and restores inheritance from the memory verse's system-wide topics.
    """

    topics = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.all(),
        many=True,
        allow_empty=True,
    )

    class Meta:
        model = UserVerse
        fields = ["topics"]

    def validate_topics(self, topics):
        """
        Ensure all supplied PKs resolve to real Topic instances.

        PrimaryKeyRelatedField already handles this, but we surface a
        cleaner error message here if the list is non-empty but invalid.

        Parameters
        ----------
        topics : list[Topic]
            The resolved Topic instances from the submitted PKs.

        Returns
        -------
        list[Topic]
            The validated topic list.
        """

        return topics

    def update(self, instance: UserVerse, validated_data: dict) -> UserVerse:
        """
        Replace the user's topic overrides with the supplied list.

        Parameters
        ----------
        instance : UserVerse
            The UserVerse being updated.
        validated_data : dict
            Validated data containing the new topic list.

        Returns
        -------
        UserVerse
            The updated UserVerse instance.
        """

        instance.topics.set(validated_data["topics"])

        return instance
