"""
Views for the verses app.
"""

# third_party_packages
from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

# other_apps_packages
from core.verses.bible_api.exceptions import (
    BibleApiUnavailableError,
    BibleApiVerseNotFoundError,
)
from core.verses.exceptions import VerseValidationError
from core.verses.models import MemoryVerse
from core.verses.serializers import (
    MemoryVerseAdminSerializer,
    MemoryVerseCreateSerializer,
    MemoryVerseSerializer,
)


class MemoryVerseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing MemoryVerse resources.
    """

    queryset = MemoryVerse.objects.select_related(
        "verse_start",
        "verse_end",
        "created_by",
    )

    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        """
        Return the appropriate serializer class for the current action.

        Returns
        -------
        type
            The serializer class to be used for the request.
        """

        if self.action == "create":
            return MemoryVerseCreateSerializer
        if self.action == "partial_update":
            return MemoryVerseAdminSerializer
        return MemoryVerseSerializer

    def get_permissions(self):
        """
        Return the permission classes based on the current action.

        Returns
        -------
        list
            List of permission instances for the request.
        """

        if self.action in ["partial_update", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Return the queryset for MemoryVerse objects.

        Returns
        -------
        QuerySet
            The queryset used for retrieving MemoryVerse records.
        """

        return self.queryset

    def create(self, request, *args, **kwargs):
        """
        Create a new MemoryVerse instance from validated request data.

        Parameters
        ----------
        request : Request
            The incoming HTTP request.
        *args
            Additional positional arguments.
        **kwargs
            Additional keyword arguments.

        Returns
        -------
        Response
            The HTTP response containing the created MemoryVerse data or an error message.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            memory_verse = serializer.save(created_by=request.user)
        except BibleApiVerseNotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        except BibleApiUnavailableError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except VerseValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        output = MemoryVerseSerializer(memory_verse)

        return Response(output.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Reject full updates and instruct clients to use PATCH instead.

        Parameters
        ----------
        request : Request
            The incoming HTTP request.
        *args
            Additional positional arguments.
        **kwargs
            Additional keyword arguments.

        Returns
        -------
        Response
            HTTP 405 response indicating PUT is not allowed.
        """

        return Response(
            {"detail": "PUT method not allowed. Use PATCH instead."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
