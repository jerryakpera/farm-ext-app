"""
Pagination configuration for reusability across the project.
"""

# third_party_packages
from rest_framework.pagination import PageNumberPagination


class StandardResultsPagination(PageNumberPagination):
    """
    Default pagination used across all list endpoints.
    """

    page_size_query_param = "page_size"
    max_page_size = 100
