"""
Views for the verses app.
"""

# third_party_packages
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

# other_apps_packages
from core.verses.bible_api.client import _format_reference, fetch_verse_text
from core.verses.bible_api.exceptions import (
    BibleApiUnavailableError,
    BibleApiVerseNotFoundError,
)
from core.verses.exceptions import VerseValidationError
from core.verses.filters import MemoryVerseFilterSet
from core.verses.models import MemoryVerse, UserVerse
from core.verses.serializers import (
    MemoryVerseAdminSerializer,
    MemoryVerseCreateSerializer,
    MemoryVerseSerializer,
    UserVerseReadSerializer,
    VersePreviewSerializer,
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

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = MemoryVerseFilterSet
    search_fields = ["verse_start__text", "verse_start__book"]

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

    @action(
        detail=False,
        methods=["get"],
        url_path="preview",
        permission_classes=[IsAuthenticated],
    )
    def preview(self, request):
        """
        Fetch and return a verse text preview from the Bible API.

        Parameters
        ----------
        request : Request
            The incoming HTTP request containing the following query parameters.

        Returns
        -------
        Response
            200 - { "text": "...", "reference": "Genesis 1:1" }
            400 - { "detail": "..." }  validation errors
            404 - { "detail": "..." }  verse not found
            503 - { "detail": "..." }  Bible API unavailable.
        """
        serializer = VersePreviewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        book = data["book"]
        chapter = data["chapter"]
        verse_start = data["verse_start"]
        verse_end = data.get("verse_end")
        version = data["version"]

        try:
            text = fetch_verse_text(
                translation=version,
                book=book,
                chapter=chapter,
                verse_start=verse_start,
                verse_end=verse_end,
            )
        except BibleApiVerseNotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except BibleApiUnavailableError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        reference = _format_reference(book, chapter, verse_start, verse_end)

        return Response(
            {"text": text, "reference": reference}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_path="learn-next")
    def learn_next(self, request, pk=None):
        """
        Add this memory verse to the user's library at the front of the backlog.

        Parameters
        ----------
        request : Request
            The HTTP request.
        pk : int
            Primary key of the MemoryVerse.

        Returns
        -------
        Response
            Serialized representation of the created UserVerse, or 400
            if the verse is already in the user's library.
        """

        memory_verse = self.get_object()

        if UserVerse.objects.filter(
            user=request.user, memory_verse=memory_verse
        ).exists():
            return Response(
                {"detail": "This verse is already in your library."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_verse = UserVerse.objects.create(
            user=request.user,
            memory_verse=memory_verse,
            order=UserVerse.learn_next_order_for_user(request.user),
        )

        return Response(
            UserVerseReadSerializer(user_verse, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="learn-last")
    def learn_last(self, request, pk=None):
        """
        Add this memory verse to the user's library at the back of the backlog.

        Parameters
        ----------
        request : Request
            The HTTP request.
        pk : int
            Primary key of the MemoryVerse.

        Returns
        -------
        Response
            Serialized representation of the created UserVerse, or 400
            if the verse is already in the user's library.
        """

        memory_verse = self.get_object()

        if UserVerse.objects.filter(
            user=request.user, memory_verse=memory_verse
        ).exists():
            return Response(
                {"detail": "This verse is already in your library."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_verse = UserVerse.objects.create(
            user=request.user,
            memory_verse=memory_verse,
            order=UserVerse.next_order_for_user(request.user),
        )

        return Response(
            UserVerseReadSerializer(user_verse, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
