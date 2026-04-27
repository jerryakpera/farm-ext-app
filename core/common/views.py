"""
Views for the common app.
"""

# django_packages
from django.shortcuts import render


def index(request):
    """
    Render the application landing page.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        Rendered response for the index page.
    """

    return render(
        context={},
        request=request,
        template_name="common/pages/index.html",
    )
