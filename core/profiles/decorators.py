"""
Decorators for the `profiles` app.
"""

# python_packages
from functools import wraps

# django_packages
from django.shortcuts import redirect


def guest_only(view_func):
    """
    Restrict access to guest-only pages for authenticated users.

    Parameters
    ----------
    view_func : callable
        The view function to be wrapped.

    Returns
    -------
    callable
        The wrapped view function that redirects authenticated users.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        """
        Execute the wrapped view with guest-only access control.

        Parameters
        ----------
        request : HttpRequest
            The incoming HTTP request.
        *args
            Positional arguments passed to the view.
        **kwargs
            Keyword arguments passed to the view.

        Returns
        -------
        HttpResponse
            Redirect response for authenticated users or the original view response.
        """
        if request.user.is_authenticated:
            return redirect("common:index")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
