"""
Settings for the test suite.

Inherits from base and overrides anything that should behave
differently during testing — fast password hashing, in-memory
email, synchronous Celery tasks, and a separate test database.
"""

# app_packages
from .base import *  # noqa: F401, F403
from .base import BASE_DIR


# ─── Core ────────────────────────────────────────────────────────────────────

DEBUG = False
SECRET_KEY = "test-secret-key-not-used-in-production"  # noqa: S105

# ─── Database ────────────────────────────────────────────────────────────────
# Use the same DB engine but with a test_ prefix handled by pytest-django.
# If you want fully in-memory, swap to sqlite for speed.

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# ─── Password hashing ────────────────────────────────────────────────────────
# MD5 is intentionally weak — only used in tests for speed.

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# ─── Email ───────────────────────────────────────────────────────────────────
# Catch all outgoing emails in memory — nothing is sent.

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# ─── Celery ──────────────────────────────────────────────────────────────────
# Run tasks synchronously and inline — no worker or broker needed.

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ─── Media & Static ──────────────────────────────────────────────────────────

MEDIA_ROOT = BASE_DIR / "test_media"

# ─── Mailtrap ────────────────────────────────────────────────────────────────

MAILTRAP_API_KEY = "test-key"
MAILTRAP_USE_SANDBOX = True
MAILTRAP_INBOX_ID = "0"
