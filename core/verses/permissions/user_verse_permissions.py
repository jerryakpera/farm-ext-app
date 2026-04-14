"""
Custom DRF permissions for the verses app.
"""

# third_party_packages
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Allow access only to the owner of a UserVerse.

    Assumes the object has a ``user`` attribute that references the
    owning user. Applied on top of IsAuthenticated — authentication
    is always required first.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """
        Return True only if the requesting user owns the object.

        Parameters
        ----------
        request : Request
            The HTTP request instance.
        view : View
            The view handling the request.
        obj : UserVerse
            The object being accessed.

        Returns
        -------
        bool
            True if request.user is the owner of the object, otherwise False.
        """
        return obj.user == request.user
