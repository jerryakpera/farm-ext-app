#!/usr/bin/env python

"""
Django's command-line utility for administrative tasks.
"""

# python_packages
import os
import sys

# other_apps_packages
from config.settings import base


def main():
    """
    Run administrative tasks.
    """

    if base.DEBUG:
        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE",
            "config.settings.local",
        )
    else:
        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE",
            "config.settings.production",
        )

    try:
        # django_packages
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
