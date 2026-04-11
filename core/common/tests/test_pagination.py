"""
Tests for core.common.pagination.
"""

# third_party_packages
import pytest

# other_apps_packages
from core.common.pagination import StandardResultsPagination


@pytest.mark.django_db
def test_pagination_default_page_size():
    """
    StandardResultsPagination carries the correct default page size.
    """

    paginator = StandardResultsPagination()
    assert paginator.page_size == 50


def test_pagination_max_page_size():
    """
    Hard cap on page size is 100.
    """

    paginator = StandardResultsPagination()
    assert paginator.max_page_size == 100


def test_pagination_query_param():
    """
    Client can override page size via the page_size query param.
    """

    paginator = StandardResultsPagination()
    assert paginator.page_size_query_param == "page_size"
