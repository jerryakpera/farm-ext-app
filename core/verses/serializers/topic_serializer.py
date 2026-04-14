"""
Serializers for the `verses` app.
"""

# third_party_packages
from rest_framework import serializers

# other_apps_packages
from core.verses.models import Topic


class TopicSerializer(serializers.ModelSerializer):
    """
    Read-only representation of a Topic.
    """

    class Meta:
        model = Topic
        fields = ["id", "name"]
        read_only_fields = fields
