"""
Serializers for the analytics app.
"""

# third_party_packages
from rest_framework import serializers


class DashboardWhitelistCheckSerializer(serializers.Serializer):
    """
    Validates the email query parameter supplied to the auth check endpoint.
    """

    email = serializers.EmailField()
