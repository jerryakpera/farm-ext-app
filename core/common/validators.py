"""
Util functions for the `core` app.
"""

# django_packages
from django.core.exceptions import ValidationError


def validate_image_size(image):  # pragma: no cover
    """
    Validate the size of the uploaded image.

    Parameters
    ----------
    image : InMemoryUploadedFile
        The uploaded image file.
    """

    max_size_mb = 2

    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Image size cannot exceed {max_size_mb} MB.")


def validate_image_format(image):  # pragma: no cover
    """
    Validate the format of the uploaded image.

    Parameters
    ----------
    image : InMemoryUploadedFile
        The uploaded image file.
    """

    valid_extensions = ["jpg", "jpeg", "png", "webp"]
    ext = image.name.split(".")[-1].lower()

    if ext not in valid_extensions:
        raise ValidationError(f"Unsupported file extension: {ext}.")
