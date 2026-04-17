"""
Serializers for the `custom_user` app.
"""

# third_party_packages
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """
    Serializer for authenticating a user with email and password.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for logging out a user by invalidating their refresh token.
    """

    refresh = serializers.CharField(write_only=True)
