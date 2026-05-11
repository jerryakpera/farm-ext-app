# core/common/serializers.py

"""
Serializers for the common app.
"""

# third_party_packages
from rest_framework import serializers

# app_packages
from .models import Ward


class WardSerializer(serializers.ModelSerializer):
    """
    Serializer for the Ward model.
    """

    class Meta:
        model = Ward
        fields = ["id", "name"]
