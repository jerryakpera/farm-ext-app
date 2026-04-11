"""
Root conftest.py — fixtures available to the entire test suite.
"""

# third_party_packages
import pytest

from faker import Faker
from rest_framework.test import APIClient


fake = Faker()


@pytest.fixture
def api_client():
    """
    Return an unauthenticated DRF API test client.

    Returns
    -------
    APIClient
        A fresh unauthenticated client for each test.
    """

    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """
    Return an API client authenticated as ``user``.

    Parameters
    ----------
    api_client : APIClient
        The base unauthenticated client fixture.
    user : django.contrib.auth.models.User
        A persisted user fixture.

    Returns
    -------
    APIClient
        Client with JWT Authorization header set.
    """

    # third_party_packages
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    return api_client


@pytest.fixture
def user(db):
    """
    Create and return a standard active user.

    Parameters
    ----------
    db : pytest-django fixture
        Grants database access for this test.

    Returns
    -------
    django.contrib.auth.models.User
        A persisted, active user instance.
    """

    # django_packages
    from django.contrib.auth import get_user_model

    User = get_user_model()

    return User.objects.create_user(
        email=fake.email(),
        password="Testpass123!",
    )


@pytest.fixture
def superuser(db):
    """
    Create and return a superuser.

    Parameters
    ----------
    db : pytest-django fixture
        Grants database access for this test.

    Returns
    -------
    django.contrib.auth.models.User
        A persisted superuser instance.
    """

    # django_packages
    from django.contrib.auth import get_user_model

    User = get_user_model()

    return User.objects.create_superuser(
        email=fake.email(),
        password="Testpass123!",
    )
