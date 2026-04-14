"""
FilterSets for the verses app.
"""

# third_party_packages
import django_filters

from django_filters import rest_framework as filters

# app_packages
from ..models.topic import Topic


class TopicFilterSet(filters.FilterSet):
    """
    Supports filtering and ordering the topic list.
    """

    name = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Name",
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("name", "name"),
            ("created_at", "created_at"),
        ),
    )

    class Meta:
        model = Topic
        fields = ["name"]
