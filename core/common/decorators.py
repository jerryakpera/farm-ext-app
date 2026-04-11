"""
Reusable rate-limit decorators for sensitive API endpoints.
"""

# third_party_packages
from django_ratelimit.decorators import ratelimit


# Authentication endpoints — 5 attempts per minute per IP.
rate_limit_auth = ratelimit(
    key="ip",
    rate="5/m",
    method="POST",
    block=True,
)

# Password reset / sensitive mutations — 3 per hour per IP.
rate_limit_sensitive = ratelimit(
    key="ip",
    rate="3/h",
    method="POST",
    block=True,
)
