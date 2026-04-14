"""
Views for UserVerse.
"""

# python_packages
from datetime import date

# third_party_packages
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

# app_packages
from ..filters import UserVerseFilterSet
from ..models.user_verse import UserVerse
from ..permissions import IsOwner
from ..serializers import (
    TallyIncrementSerializer,
    UserVerseOrderSerializer,
    UserVerseReadSerializer,
    UserVerseTopicsSerializer,
    UserVerseWriteSerializer,
)
from ..validations import validate_daily_verse_limit


class UserVerseViewSet(ModelViewSet):
    """
    CRUD + custom actions for a user's personal verse library.

    Endpoints:
    GET    /user-verses/                  list
    POST   /user-verses/                  create (add to backlog)
    GET    /user-verses/<pk>/             retrieve
    PATCH  /user-verses/<pk>/             partial_update (order only)
    DELETE /user-verses/<pk>/             destroy
    POST   /user-verses/<pk>/learn-today/ mark verse as started today
    POST   /user-verses/<pk>/learn-next/  requeue verse to front of backlog
    POST   /user-verses/<pk>/tally/       increment recitation tally
    PATCH  /user-verses/<pk>/topics/      set user topic overrides
    """

    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserVerseFilterSet
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        """
        Return only the authenticated user's verses, with related data
        pre-fetched to avoid N+1 queries.

        Returns
        -------
        QuerySet[UserVerse]
            Queryset of UserVerse objects belonging to the authenticated user.
        """

        return (
            UserVerse.objects.filter(user=self.request.user)
            .select_related(
                "memory_verse__verse_start",
                "memory_verse__verse_end",
            )
            .prefetch_related(
                "memory_verse__topics",
                "topics",
            )
        )

    def get_serializer_class(self):
        """
        Route to the correct serializer based on the action.

        Returns
        -------
        type[Serializer]
            Serializer class for the current view action.
        """

        if self.action == "create":
            return UserVerseWriteSerializer
        if self.action == "partial_update":
            return UserVerseOrderSerializer
        if self.action == "tally":
            return TallyIncrementSerializer
        if self.action == "topics":
            return UserVerseTopicsSerializer

        return UserVerseReadSerializer

    # ------------------------------------------------------------------ #
    # Standard actions                                                     #
    # ------------------------------------------------------------------ #

    def create(self, request, *args, **kwargs):
        """
        Add a verse to the user's backlog.

        Parameters
        ----------
        request : Request
            The HTTP request containing the payload.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Response
            Serialized representation of the created UserVerse.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_verse = serializer.save()

        return Response(
            UserVerseReadSerializer(user_verse, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        """
        Update the order of a UserVerse in the backlog queue.

        Parameters
        ----------
        request : Request
            The HTTP request containing update data.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Response
            Serialized representation of the updated UserVerse.
        """

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            UserVerseReadSerializer(
                instance,
                context={
                    "request": request,
                },
            ).data
        )

    # Disable full PUT — partial_update (PATCH) is the only write path
    # for an existing UserVerse outside of the dedicated actions below.
    def update(self, request, *args, **kwargs):
        """
        Disable full update (PUT) for UserVerse.

        Parameters
        ----------
        request : Request
            The HTTP request.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Response
            HTTP 405 Method Not Allowed response.
        """

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # ------------------------------------------------------------------ #
    # Custom actions                                                       #
    # ------------------------------------------------------------------ #

    @action(detail=True, methods=["post"], url_path="learn-today")
    def learn_today(self, request, pk=None):
        """
        Mark a verse as started for today and enforce daily learning limits.

        Parameters
        ----------
        request : Request
            The HTTP request.
        pk : int
            Primary key of the UserVerse.

        Returns
        -------
        Response
            Updated UserVerse representation on success.
        """

        instance = self.get_object()

        if instance.learned_at is not None:
            return Response(
                {"detail": "This verse has already been started."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Raises ValidationError → 400 if another verse was started today.
        validate_daily_verse_limit(request.user)

        instance.learned_at = date.today()
        instance.save(update_fields=["learned_at"])

        return Response(
            UserVerseReadSerializer(instance, context={"request": request}).data
        )

    @action(detail=True, methods=["post"], url_path="learn-next")
    def learn_next(self, request, pk=None):
        """
        Move a verse to the front of the user's backlog queue.

        Parameters
        ----------
        request : Request
            The HTTP request.
        pk : int
            Primary key of the UserVerse.

        Returns
        -------
        Response
            Updated UserVerse representation.
        """
        instance = self.get_object()
        instance.order = UserVerse.learn_next_order_for_user(request.user)
        instance.save(update_fields=["order"])

        return Response(
            UserVerseReadSerializer(instance, context={"request": request}).data
        )

    @action(detail=True, methods=["post"], url_path="tally")
    def tally(self, request, pk=None):
        """
        Increment the recitation tally for a verse.

        Parameters
        ----------
        request : Request
            The HTTP request containing the increment payload.
        pk : int
            Primary key of the UserVerse.

        Returns
        -------
        Response
            Updated UserVerse representation.
        """

        instance = self.get_object()
        serializer = TallyIncrementSerializer(
            data=request.data,
            context={"user_verse": instance},
        )
        serializer.is_valid(raise_exception=True)

        count = serializer.validated_data["count"]
        instance.tally += count
        instance.last_practiced_at = date.today()

        # Stamp learned_at on the very first recitation if somehow missed.
        if instance.learned_at is None:
            instance.learned_at = date.today()

        instance.save(update_fields=["tally", "last_practiced_at", "learned_at"])

        return Response(
            UserVerseReadSerializer(instance, context={"request": request}).data
        )

    @action(detail=True, methods=["patch"], url_path="topics")
    def topics(self, request, pk=None):
        """
        Update or clear user-specific topic overrides for a verse.

        Parameters
        ----------
        request : Request
            The HTTP request containing topic data.
        pk : int
            Primary key of the UserVerse.

        Returns
        -------
        Response
            Updated UserVerse representation.
        """

        instance = self.get_object()
        serializer = UserVerseTopicsSerializer(
            instance,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            UserVerseReadSerializer(instance, context={"request": request}).data
        )
