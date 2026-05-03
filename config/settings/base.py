"""
Django settings for farm-ext project.
"""

# python_packages
import os

from pathlib import Path

# third_party_packages
from decouple import config


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


ENV = config("ENV", default="production")

IS_PRODUCTION = ENV == "production"

LOGGING_TOKEN = config("LOGGING_TOKEN", default=None)
INGESTING_HOST = config("INGESTING_HOST", default=None)

SECRET_KEY = config("SECRET_KEY")
DEBUG = True if ENV == "development" else False
ALLOWED_HOSTS = config("HOSTS_ALLOWED").split(" ")


# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_use_email_as_username.apps.DjangoUseEmailAsUsernameConfig",
    "core.custom_user.apps.CustomUserConfig",
    "formtools",
    "storages",
]

LOCAL_APPS = [
    "core.common",
    "core.profiles",
    "core.farms",
    "core.questions",
    "core.advisory",
    "core.visits",
]

INSTALLED_APPS = (
    DJANGO_APPS
    + THIRD_PARTY_APPS
    + LOCAL_APPS
    + [
        "django_cleanup.apps.CleanupConfig",  # must be last
    ]
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "core", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "profiles:login"
LOGOUT_REDIRECT_URL = "profiles:login"

AUTH_USER_MODEL = "custom_user.User"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# ── Static files ────────────────────────────────────────────────────────────
WHITENOISE_USE_BROTLI = True
WHITENOISE_AUTOREFRESH = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "core" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")

AWS_LOCATION = config("AWS_LOCATION")

AWS_S3_FILE_OVERWRITE = False
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOME_DOMAIN = "%s.s3.amazonaws.com" % config("AWS_STORAGE_BUCKET_NAME")
