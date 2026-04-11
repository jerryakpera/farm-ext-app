"""
Docstring for config.settings.production.
"""

# third_party_packages
from decouple import config

# app_packages
from .base import *
from .base import REST_FRAMEWORK


API_URL = config("API_BASE_URL")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": "localhost",
    }
}

EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ─── Security — production only ───────────────────────────────────────────────

# Force all cookies over HTTPS only.
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Redirect all HTTP traffic to HTTPS.
# If terminating SSL at a load balancer or reverse proxy, set this to False
# and let the proxy handle the redirect instead.
SECURE_SSL_REDIRECT = True

# Tell Django to trust the X-Forwarded-Proto header from your proxy.
# Required when SSL is terminated upstream (Railway, Render, Nginx, etc.).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS — tell browsers to only ever connect via HTTPS.
# Start with a short value (300), verify everything works,
# then increase to 31536000 (1 year) before submitting to the preload list.
SECURE_HSTS_SECONDS = 300  # ← increase to 31536000 once confirmed
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session expires when the browser closes — no persistent session cookies.
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 days if you need persistence
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # flip to True for stricter sessions

# Prevent session fixation.
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
