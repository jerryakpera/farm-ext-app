"""
Serializers for the `verses` app.
"""

# third_party_packages
from rest_framework import serializers

# app_packages
from ..models.topic import Topic


class TopicSerializer(serializers.ModelSerializer):
    """
    Read and write representation of a Topic.

    Validation:
    - Name may not be blank or whitespace-only.
    - Name must be unique regardless of case (Faith, faith, FAITH are duplicates).
    - Name is stored in title case for consistency.
    """

    class Meta:
        model = Topic
        fields = ["id", "name"]

    def validate_name(self, value: str) -> str:
        """
        Enforce non-blank and case-insensitive uniqueness on topic name.

        Parameters
        ----------
        value : str
            The submitted topic name.

        Returns
        -------
        str
            The name normalised to title case.
        """

        value = value.strip()

        if not value:
            raise serializers.ValidationError("Topic name may not be blank.")

        normalised = value.title()

        # On updates, exclude the current instance from the uniqueness check.
        qs = Topic.objects.filter(name__iexact=normalised)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                f'A topic named "{normalised}" already exists.'
            )

        return normalised
