"""
Util functions for the `core` app.
"""

# python_packages
import os
import uuid

# django_packages
from django.utils.text import slugify


def file_upload_path(instance, filename):  # pragma: no cover
    """
    Generate a unique file path for uploaded files.

    Parameters
    ----------
    instance : Model instance
        The model instance.
    filename : str
        The original filename of the uploaded file.

    Returns
    -------
    str
        The unique file path for the file.
    """

    # extract file extension
    ext = filename.split(".")[-1]

    # generate unique filename
    filename = f"{uuid.uuid4().hex}.{ext}"

    # Get the folder name from the instance
    folder_name = slugify(str(instance._meta.verbose_name_plural))

    instance_id = instance.id if instance else "none"

    return os.path.join(
        folder_name,
        str(instance_id),
        filename,
    )
